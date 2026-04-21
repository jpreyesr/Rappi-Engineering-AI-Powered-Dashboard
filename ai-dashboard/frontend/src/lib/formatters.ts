const numberFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 0,
});

const compactFormatter = new Intl.NumberFormat("en-US", {
  notation: "compact",
  maximumFractionDigits: 1,
});

const dateTimeFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

export function formatNumber(value: number | string | null): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  if (typeof value === "string") {
    return value;
  }
  return numberFormatter.format(value);
}

export function formatCompactNumber(value: number): string {
  return compactFormatter.format(value);
}

export function formatDateTime(value: string | null): string {
  if (!value) {
    return "-";
  }
  return dateTimeFormatter.format(new Date(value));
}
