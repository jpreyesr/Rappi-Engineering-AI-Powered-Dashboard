from __future__ import annotations

import csv
import hashlib
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from duckdb import DuckDBPyConnection

from app.core.config import DASHBOARD_ROOT
from app.core.constants import (
    AVAILABILITY_ENRICHED_TABLE,
    AVAILABILITY_POINTS_TABLE,
    INGESTION_FILE_REPORTS_TABLE,
    LOAD_METADATA_TABLE,
)
from app.db.duckdb_client import DuckDBClient
from app.schemas.data import DataLoadResponse, DataStatusResponse, IngestionFileReport


class IngestionError(Exception):
    def __init__(self, message: str, reports: list[IngestionFileReport] | None = None) -> None:
        super().__init__(message)
        self.reports = reports or []


class IngestionService:
    AVAILABILITY_PREFIX = ("Plot name", "metric (sf_metric)", "Value Prefix", "Value Suffix")

    def __init__(self, db: DuckDBClient) -> None:
        self.db = db
        self.extracted_dir = DASHBOARD_ROOT / "data" / "extracted"
        self.raw_dir = DASHBOARD_ROOT / "data" / "raw"

    def load(self) -> DataLoadResponse:
        source_files, files_seen, source_dir = self._discover_sources()
        reports: list[IngestionFileReport] = []
        availability_points: list[tuple[datetime, str, float, str]] = []
        raw_tables: set[str] = set()

        for path in source_files:
            if path.suffix.lower() != ".csv":
                reports.append(IngestionFileReport(file_name=path.name, status="skipped_non_csv"))
                continue
            if path.stat().st_size == 0:
                reports.append(IngestionFileReport(file_name=path.name, status="skipped_empty"))
                continue

            header = self._read_header(path)
            if self._is_availability_csv(header):
                report, points = self._parse_availability_csv(path, header)
                reports.append(report)
                availability_points.extend(points)
            else:
                report = self._load_raw_csv(path)
                reports.append(report)
                if report.table_name:
                    raw_tables.add(report.table_name)

        if not availability_points:
            errors = ["No analytical availability points were produced from valid CSV files."]
            raise IngestionError(errors[0], reports=reports)

        clean_points_loaded = len({(timestamp, metric) for timestamp, metric, _, _ in availability_points})
        tables_created = self._replace_analytics_tables(availability_points, reports, raw_tables)
        loaded_reports = [report for report in reports if report.status in {"loaded", "loaded_raw"}]
        skipped_reports = [report for report in reports if report.status not in {"loaded", "loaded_raw"}]
        timestamps = [point[0] for point in availability_points]
        errors = [error for report in reports for error in report.errors]

        return DataLoadResponse(
            status="loaded",
            source_dir=str(source_dir),
            files_seen=files_seen,
            files_loaded=len(loaded_reports),
            files_skipped=len(skipped_reports),
            points_loaded=clean_points_loaded,
            tables_created=tables_created,
            min_timestamp=min(timestamps),
            max_timestamp=max(timestamps),
            errors=errors,
            file_reports=reports,
        )

    def status(self) -> DataStatusResponse:
        source_dir = self.extracted_dir if self.extracted_dir.exists() else DASHBOARD_ROOT / "data" / "extracted"
        files_seen = len([path for path in source_dir.iterdir() if path.is_file()]) if source_dir.exists() else 0

        try:
            with self.db.connect(read_only=True) as connection:
                tables = {row[0] for row in connection.execute("show tables").fetchall()}
                if LOAD_METADATA_TABLE not in tables:
                    return DataStatusResponse(status="not_loaded", source_dir=str(source_dir), files_seen=files_seen)

                metadata = connection.execute(
                    f"""
                    select loaded_at, files_count, points_count, min_timestamp, max_timestamp, errors
                    from {LOAD_METADATA_TABLE}
                    order by loaded_at desc
                    limit 1
                    """
                ).fetchone()
                recent_files = self._read_recent_file_reports(connection, tables)
                loaded_tables = sorted(tables)
        except FileNotFoundError:
            return DataStatusResponse(status="not_loaded", source_dir=str(source_dir), files_seen=files_seen)

        if not metadata:
            return DataStatusResponse(status="not_loaded", source_dir=str(source_dir), files_seen=files_seen)

        loaded_at, files_count, points_count, min_timestamp, max_timestamp, errors = metadata
        return DataStatusResponse(
            status="loaded",
            source_dir=str(source_dir),
            files_seen=files_seen,
            files_loaded=files_count,
            files_skipped=max(files_seen - files_count, 0),
            points_loaded=points_count,
            tables_created=loaded_tables,
            min_timestamp=min_timestamp,
            max_timestamp=max_timestamp,
            last_loaded_at=loaded_at,
            errors=self._split_errors(errors),
            recent_files=recent_files,
        )

    def _discover_sources(self) -> tuple[list[Path], int, Path]:
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        extracted_files = sorted(path for path in self.extracted_dir.iterdir() if path.is_file())
        if extracted_files:
            return extracted_files, len(extracted_files), self.extracted_dir

        zip_files = sorted(path for path in self.raw_dir.glob("*.zip") if path.is_file()) if self.raw_dir.exists() else []
        if not zip_files:
            raise IngestionError("No CSV files found in data/extracted and no zip fallback found in data/raw.")

        self._extract_zip(zip_files[0], self.extracted_dir)
        extracted_files = sorted(path for path in self.extracted_dir.iterdir() if path.is_file())
        if not extracted_files:
            raise IngestionError(f"Zip fallback {zip_files[0].name} did not contain extractable files.")
        return extracted_files, len(extracted_files), self.extracted_dir

    def _extract_zip(self, zip_path: Path, destination: Path) -> None:
        with zipfile.ZipFile(zip_path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                member_path = Path(member.filename)
                if member_path.is_absolute() or ".." in member_path.parts:
                    continue
                target = destination / member_path.name
                with archive.open(member) as source, target.open("wb") as output:
                    output.write(source.read())

    def _read_header(self, path: Path) -> list[str]:
        try:
            with path.open(newline="", encoding="utf-8-sig") as handle:
                return next(csv.reader(handle), [])
        except (OSError, UnicodeDecodeError, csv.Error):
            return []

    def _is_availability_csv(self, header: list[str]) -> bool:
        return len(header) > len(self.AVAILABILITY_PREFIX) and tuple(header[:4]) == self.AVAILABILITY_PREFIX

    def _parse_availability_csv(
        self,
        path: Path,
        header: list[str],
    ) -> tuple[IngestionFileReport, list[tuple[datetime, str, float, str]]]:
        points: list[tuple[datetime, str, float, str]] = []
        errors: list[str] = []
        parsed_timestamps: list[datetime | None] = [self._parse_timestamp(column) for column in header[4:]]

        try:
            with path.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.reader(handle)
                next(reader, None)
                for row_number, row in enumerate(reader, start=2):
                    if len(row) < 5:
                        errors.append(f"row {row_number}: expected timestamp values")
                        continue
                    metric = row[1].strip() if len(row) > 1 else ""
                    if not metric:
                        errors.append(f"row {row_number}: missing metric")
                        continue
                    for offset, raw_value in enumerate(row[4:]):
                        timestamp = parsed_timestamps[offset] if offset < len(parsed_timestamps) else None
                        if timestamp is None:
                            if offset < 5:
                                errors.append(f"column {offset + 5}: invalid timestamp")
                            continue
                        value = self._parse_float(raw_value)
                        if value is None:
                            continue
                        points.append((timestamp, metric, value, path.name))
        except (OSError, UnicodeDecodeError, csv.Error) as exc:
            return (
                IngestionFileReport(
                    file_name=path.name,
                    status="failed_parse",
                    errors=[f"{type(exc).__name__}: {exc}"],
                ),
                [],
            )

        return (
            IngestionFileReport(
                file_name=path.name,
                status="loaded",
                table_name=AVAILABILITY_POINTS_TABLE,
                rows_loaded=1,
                points_loaded=len(points),
                errors=errors[:20],
            ),
            points,
        )

    def _load_raw_csv(self, path: Path) -> IngestionFileReport:
        header = self._read_header(path)
        table_name = f"raw_{self._schema_hash(header)}"
        try:
            with self.db.connect(read_only=False) as connection:
                connection.execute(
                    f"""
                    create or replace table {table_name} as
                    select * from read_csv_auto(?, ignore_errors = true, union_by_name = true)
                    """,
                    [str(path)],
                )
                rows_loaded = connection.execute(f"select count(*) from {table_name}").fetchone()[0]
        except Exception as exc:
            return (
                IngestionFileReport(
                    file_name=path.name,
                    status="failed_schema",
                    table_name=None,
                    errors=[f"{type(exc).__name__}: {exc}"],
                )
            )

        return IngestionFileReport(
            file_name=path.name,
            status="loaded_raw",
            table_name=table_name,
            rows_loaded=rows_loaded,
        )

    def _replace_analytics_tables(
        self,
        points: list[tuple[datetime, str, float, str]],
        reports: list[IngestionFileReport],
        raw_tables: set[str],
    ) -> list[str]:
        loaded_at = datetime.now()
        errors = [error for report in reports for error in report.errors]
        tables_created = [
            AVAILABILITY_POINTS_TABLE,
            AVAILABILITY_ENRICHED_TABLE,
            LOAD_METADATA_TABLE,
            INGESTION_FILE_REPORTS_TABLE,
            *sorted(raw_tables),
        ]

        with self.db.connect(read_only=False) as connection:
            connection.execute("begin transaction")
            try:
                self._create_core_tables(connection)
                connection.execute(
                    """
                    create temporary table availability_points_staging (
                        timestamp timestamp,
                        metric varchar,
                        visible_stores double,
                        source_file varchar
                    )
                    """
                )
                connection.executemany(
                    f"""
                    insert into availability_points_staging
                    (timestamp, metric, visible_stores, source_file)
                    values (?, ?, ?, ?)
                    """,
                    points,
                )
                connection.execute(
                    f"""
                    insert into {AVAILABILITY_POINTS_TABLE}
                    (timestamp, metric, visible_stores, source_file)
                    select
                        timestamp,
                        metric,
                        avg(visible_stores) as visible_stores,
                        min(source_file) as source_file
                    from availability_points_staging
                    group by timestamp, metric
                    order by timestamp, metric
                    """
                )
                connection.execute(
                    f"""
                    create or replace table {AVAILABILITY_ENRICHED_TABLE} as
                    select
                        timestamp,
                        metric,
                        visible_stores,
                        source_file,
                        lag(visible_stores) over (partition by metric order by timestamp, source_file) as previous_visible_stores,
                        visible_stores - lag(visible_stores) over (partition by metric order by timestamp, source_file) as delta_visible_stores,
                        date_diff(
                            'second',
                            lag(timestamp) over (partition by metric order by timestamp, source_file),
                            timestamp
                        ) as interval_seconds,
                        strftime(timestamp, '%Y-%m-%d %H:%M:%S') as timestamp_label,
                        extract('hour' from timestamp) as hour_of_day,
                        strftime(timestamp, '%A') as day_of_week
                    from {AVAILABILITY_POINTS_TABLE}
                    """
                )
                min_timestamp, max_timestamp = connection.execute(
                    f"select min(timestamp), max(timestamp) from {AVAILABILITY_POINTS_TABLE}"
                ).fetchone()
                clean_points_loaded = connection.execute(f"select count(*) from {AVAILABILITY_POINTS_TABLE}").fetchone()[0]
                loaded_files = len([report for report in reports if report.status in {"loaded", "loaded_raw"}])
                connection.execute(
                    f"""
                    insert into {LOAD_METADATA_TABLE}
                    (loaded_at, files_count, points_count, min_timestamp, max_timestamp, errors)
                    values (?, ?, ?, ?, ?, ?)
                    """,
                    [loaded_at, loaded_files, clean_points_loaded, min_timestamp, max_timestamp, "\n".join(errors[:200])],
                )
                connection.executemany(
                    f"""
                    insert into {INGESTION_FILE_REPORTS_TABLE}
                    (loaded_at, file_name, status, table_name, rows_loaded, points_loaded, errors)
                    values (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            loaded_at,
                            report.file_name,
                            report.status,
                            report.table_name,
                            report.rows_loaded,
                            report.points_loaded,
                            "\n".join(report.errors),
                        )
                        for report in reports
                    ],
                )
                connection.execute("commit")
            except Exception:
                connection.execute("rollback")
                raise

        return tables_created

    def _create_core_tables(self, connection: DuckDBPyConnection) -> None:
        self._drop_relation(connection, AVAILABILITY_POINTS_TABLE)
        self._drop_relation(connection, AVAILABILITY_ENRICHED_TABLE)
        self._drop_relation(connection, LOAD_METADATA_TABLE)
        self._drop_relation(connection, INGESTION_FILE_REPORTS_TABLE)
        connection.execute(
            f"""
            create table {AVAILABILITY_POINTS_TABLE} (
                timestamp timestamp,
                metric varchar,
                visible_stores double,
                source_file varchar
            )
            """
        )
        connection.execute(
            f"""
            create table {LOAD_METADATA_TABLE} (
                loaded_at timestamp,
                files_count integer,
                points_count integer,
                min_timestamp timestamp,
                max_timestamp timestamp,
                errors varchar
            )
            """
        )
        connection.execute(
            f"""
            create table {INGESTION_FILE_REPORTS_TABLE} (
                loaded_at timestamp,
                file_name varchar,
                status varchar,
                table_name varchar,
                rows_loaded integer,
                points_loaded integer,
                errors varchar
            )
            """
        )

    def _drop_relation(self, connection: DuckDBPyConnection, name: str) -> None:
        try:
            connection.execute(f"drop view if exists {name}")
        except Exception:
            pass
        try:
            connection.execute(f"drop table if exists {name}")
        except Exception:
            pass

    def _read_recent_file_reports(
        self,
        connection: DuckDBPyConnection,
        tables: set[str],
    ) -> list[IngestionFileReport]:
        if INGESTION_FILE_REPORTS_TABLE not in tables:
            return []
        rows = connection.execute(
            f"""
            select file_name, status, table_name, rows_loaded, points_loaded, errors
            from {INGESTION_FILE_REPORTS_TABLE}
            order by loaded_at desc, file_name
            limit 50
            """
        ).fetchall()
        return [
            IngestionFileReport(
                file_name=file_name,
                status=status,
                table_name=table_name,
                rows_loaded=rows_loaded or 0,
                points_loaded=points_loaded or 0,
                errors=self._split_errors(errors),
            )
            for file_name, status, table_name, rows_loaded, points_loaded, errors in rows
        ]

    def _parse_timestamp(self, value: str) -> datetime | None:
        match = re.match(r"^[A-Za-z]{3} ([A-Za-z]{3}) (\d{2}) (\d{4}) (\d{2}:\d{2}:\d{2}) GMT([+-]\d{4})", value)
        if not match:
            return None
        month, day, year, time_value, offset = match.groups()
        try:
            parsed = datetime.strptime(f"{month} {day} {year} {time_value} {offset}", "%b %d %Y %H:%M:%S %z")
        except ValueError:
            return None
        return parsed.replace(tzinfo=None)

    def _parse_float(self, value: str) -> float | None:
        cleaned = value.strip().replace(",", "")
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    def _schema_hash(self, header: list[str]) -> str:
        prefix = "\x1f".join(column.strip().lower() for column in header[:12])
        return hashlib.sha1(prefix.encode("utf-8")).hexdigest()[:12]

    def _split_errors(self, errors: Any) -> list[str]:
        if not errors:
            return []
        if isinstance(errors, list):
            return [str(error) for error in errors if error]
        return [line for line in str(errors).splitlines() if line]
