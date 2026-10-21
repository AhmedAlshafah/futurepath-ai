
import json
import time
from urllib.request import urlopen
from urllib.parse import urlencode

BASE_URL = "https://himalayas.app/jobs/api/search"


def fetch_page(page):
    parameters = {
        "q": "data analyst",
        "worldwide": "true",
        "sort": "recent",
        "page": page
    }

    url = BASE_URL + "?" + urlencode(parameters)

    with urlopen(url, timeout=20) as response:
        return json.load(response)


# Step 1: Fetch the first page
first_page = fetch_page(1)

total = first_page["totalCount"]
limit = first_page["limit"]

# Step 2: Calculate the required number of pages
pages = (total + limit - 1) // limit

print("Total keyword search results:", total)
print("Pages to check:", pages)

# Step 3: Collect matching job records
matches = []

for page_number in range(1, pages + 1):

    if page_number == 1:
        data = first_page
    else:
        data = fetch_page(page_number)

    print(f"Checking page {page_number}...")

    for job in data["jobs"]:
        title = job["title"]

        if "data analyst" in title.lower():
            matches.append(job)

    # Small delay to avoid making requests too quickly
    if page_number < pages:
        time.sleep(0.5)


# Step 4: Remove duplicate listings

unique_jobs = {}

for job in matches:
    job_id = job.get("guid")

    if job_id:
        unique_jobs[job_id] = job

# Step 5: Display unique jobs

print("\nUnique Data Analyst listings:\n")

for job in unique_jobs.values():
    print("Job:", job["title"])
    print("Company:", job["companyName"])
    print("Link:", job["applicationLink"])
    print("-----------------------")

print("\nTitle-matching records:", len(matches))
print("Unique listings:", len(unique_jobs))
print("Duplicates removed:", len(matches) - len(unique_jobs))
print("Records missing GUID:", sum(not job.get("guid") for job in matches))
