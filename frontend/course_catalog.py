"""Load the reviewed catalog without changing the Studio's resource contract."""

import csv
from datetime import date
import math
from pathlib import Path
from urllib.parse import urlsplit

COURSE_FILE = Path(__file__).resolve().parents[1] / "data" / "course.csv"
FIELDS = {
    "skill", "cost_type", "provider", "title", "url", "duration_hours",
    "price", "currency", "last_verified",
}


def load_course_catalog(path=COURSE_FILE):
    """Return (free resources, low-cost courses); fail explicitly on invalid data.

    Read on each Streamlit run so edits are not hidden by a stale data cache.
    There is one resource per skill and cost type, matching the existing UI.
    """
    free, paid = {}, {}
    path = Path(path)
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not FIELDS.issubset(reader.fieldnames or []):
            raise ValueError(f"{path.name}: missing required catalog columns")
        for line, raw in enumerate(reader, start=2):
            try:
                if None in raw or any(value is None for value in raw.values()):
                    raise ValueError("row has the wrong number of cells")
                row = {key: value.strip() for key, value in raw.items()}
                for key in ("skill", "cost_type", "provider", "title", "url"):
                    if not row[key]:
                        raise ValueError(f"{key} is required")
                if row["cost_type"] not in ("free", "low_cost"):
                    raise ValueError("cost_type must be free or low_cost")
                url = urlsplit(row["url"])
                if url.scheme != "https" or not url.hostname or url.username or url.password:
                    raise ValueError("url must be an HTTPS provider link without credentials")
                catalog = free if row["cost_type"] == "free" else paid
                skill = row["skill"]
                if skill in catalog:
                    raise ValueError(f"duplicate {row['cost_type']} resource for {skill}")
                resource = {key: row[key] for key in ("provider", "title", "url")}
                if row["duration_hours"]:
                    hours = float(row["duration_hours"])
                    if not math.isfinite(hours) or hours <= 0:
                        raise ValueError("duration_hours must be a positive number or blank")
                    resource["duration"] = f"{hours:g} {'hour' if hours == 1 else 'hours'}"
                if catalog is paid:
                    price = float(row["price"])
                    if not math.isfinite(price) or price <= 0:
                        raise ValueError("price must be a positive number")
                    if len(row["currency"]) != 3 or not row["currency"].isupper() or not row["currency"].isalpha():
                        raise ValueError("currency must be a three-letter uppercase code")
                    checked = date.fromisoformat(row["last_verified"])
                    # Fixed English month names preserve the existing displayed note.
                    month = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")[checked.month - 1]
                    resource.update(
                        price=price, currency=row["currency"],
                        checked_on=f"{checked.day} {month} {checked.year}",
                    )
                elif row["price"] or row["currency"] or row["last_verified"]:
                    raise ValueError("free resources must leave price, currency and last_verified blank")
                catalog[skill] = resource
            except ValueError as error:
                raise ValueError(f"{path.name}, row {line}: {error}") from error
    return free, paid
