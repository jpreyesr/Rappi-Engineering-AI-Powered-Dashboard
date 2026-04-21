from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_ingestion_service
from app.schemas.data import DataLoadResponse, DataStatusResponse
from app.services.ingestion_service import IngestionError, IngestionService

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/load", response_model=DataLoadResponse)
def load_data(service: IngestionService = Depends(get_ingestion_service)) -> DataLoadResponse:
    try:
        return service.load()
    except IngestionError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "message": str(exc),
                "file_reports": [report.model_dump() for report in exc.reports],
            },
        ) from exc


@router.get("/status", response_model=DataStatusResponse)
def data_status(service: IngestionService = Depends(get_ingestion_service)) -> DataStatusResponse:
    return service.status()
