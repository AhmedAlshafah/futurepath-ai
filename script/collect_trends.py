
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

BASE_URL = "https://himalayas.app/jobs/api/search"

ROLES = [
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "Cybersecurity Analyst",
    "Cloud Engineer",
    "Software Developer"
]

MAX_PAGES = 40

output_file = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "trend_signals.csv"
)

today = datetime.now().astimezone().date().isoformat()


def fetch_page(role, page):
    params = {
        "q": role.lower(),
        "worldwide": "true",
        "sort": "recent",
        "page": page
    }

    url = BASE_URL + "?" + urlencode(params)

    with urlopen(url, timeout=20) as response:
        return json.load(response)


rows = []

for role in ROLES:
    print(f"\nChecking {role}...")

    first = fetch_page(role, 1)

    total = first["totalCount"]
    limit = first["limit"]
    pages = (total + limit - 1) // limit

    # Do not report an incomplete search as a full count.
    if pages > MAX_PAGES:
        print(f"Skipped: {pages} pages exceed the safety limit.")
        continue

    unique_jobs = {}
    inspected = 0
    missing_ids = 0

    for page in range(1, pages + 1):
        data = first if page == 1 else fetch_page(role, page)

        for job in data["jobs"]:
            inspected += 1
            title = job.get("title", "")
            guid = job.get("guid")

            if role.lower() in title.lower():
                if guid:
                    unique_jobs[guid] = job
                else:
                    missing_ids += 1

        if page < pages:
            time.sleep(0.5)

    if inspected < total or missing_ids:
        print("Incomplete results or missing IDs. Skipping.")
        continue

    count = len(unique_jobs)
    print(f"Unique title-matching listings: {count}")

    source_url = BASE_URL + "?" + urlencode({
        "q": role.lower(),
        "worldwide": "true",
        "sort": "recent"
    })

    rows.append({
        "role": role,
        "region": "himalayas_worldwide",
        "period": today,
        "metric": "title_matched_unique_remote_listings",
        "value": count,
        "source_url": source_url,
        "retrieved_at": today
    })


# Preserve existing observations from previous dates.
fieldnames = [
    "role", "region", "period", "metric",
    "value", "source_url", "retrieved_at"
]

existing = []

if output_file.exists() and output_file.stat().st_size > 0:
    with open(output_file, newline="", encoding="utf-8") as f:
        existing = list(csv.DictReader(f))

new_keys = {
    (r["role"], r["region"], r["period"], r["metric"])
    for r in rows
}

existing = [
    r for r in existing
    if (r["role"], r["region"], r["period"], r["metric"])
    not in new_keys
]

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(existing + rows)

print(f"\nSaved {len(rows)} observations to {output_file}")
