# FuturePath AI — Data Sources

## 1. Purpose

This document records the data sources used by FuturePath AI to provide evidence-based career recommendations and job-market information.

Our objective is to help university students and fresh graduates understand relevant career opportunities and the skills needed to prepare for them.

## 2. Job-Market Trend Data

**Source Name:** Himalayas Remote Jobs API

**Provider:** Himalayas

**Official Documentation:** https://himalayas.app/docs/remote-jobs-api

**API Endpoint:** https://himalayas.app/jobs/api/search

**Date Retrieved:** 2026-10-21

**Geographical Coverage:** Worldwide-friendly remote-job listings indexed by Himalayas.

**Access Method:** Public JSON API, accessed using Python's `urllib.request` library.

**API Key:** Not required for public access.

**Update Frequency:** API data is cached and refreshed approximately every 24 hours.

**Usage Conditions:** Governed by Himalayas API terms. Visible attribution to Himalayas and a link to the source are required when displaying job data.

### 2.1 Careers Covered

The preliminary MVP supports six technology careers:

1. Data Analyst
2. Data Scientist
3. Machine Learning Engineer
4. Cybersecurity Analyst
5. Cloud Engineer
6. Software Developer

### 2.2 Data Collection Process

We developed Python scripts to retrieve job-market information from the Himalayas API.

The process is:

1. Search for each selected career using its name.
2. Apply the `worldwide=true` and `sort=recent` API parameters.
3. Retrieve the available search-result pages.
4. Filter job records whose titles contain the selected career phrase, ignoring capitalization.
5. Identify unique listings using the `guid` field.
6. Count the matching records and save the results in `data/trend_signals.csv`.
7. Record the API source URL and retrieval date.

The scripts are located in:

- `script/check_himalayas.py`
- `script/collect_trends.py`

### 2.3 Initial Job-Market Observations

**Collection Date:** 21 October 2026

| Career | Unique Title-Matching Listings |
|---|---:|
| Data Analyst | 12 |
| Data Scientist | 21 |
| Machine Learning Engineer | 25 |
| Cybersecurity Analyst | 0 |
| Cloud Engineer | 4 |
| Software Developer | 10 |

These results represent a snapshot from the Himalayas worldwide-friendly remote-job search.

They are not estimates of total worldwide job vacancies or future job growth.

The zero recorded for Cybersecurity Analyst indicates that no records matched the exact title-filtering rule during this collection. Related titles may still exist.

### 2.4 Data Storage

The observations are stored in:

`data/trend_signals.csv`

The dataset contains:

- `role`: Selected career
- `region`: Source coverage label
- `period`: Observation date
- `metric`: Type of measurement
- `value`: Number of unique title-matching records
- `source_url`: Original search URL
- `retrieved_at`: Date of retrieval

The metric used is:

`title_matched_unique_remote_listings`

## 3. Career and Skills Data

**Planned Primary Source:** O*NET OnLine

**Website:** https://www.onetonline.org/

The team will research the skills associated with the six selected careers.

This information will be used to build:

`data/role_skills.csv`

Each skill record will include its career, skill name, team-assigned importance weight, supporting source URL and verification date.

The Data/Research team is currently preparing this dataset. Sources, usage conditions and skill weights will be reviewed before final integration.

## 4. Data Limitations

The current job-market dataset has several limitations:

- Himalayas does not represent every employer or job vacancy worldwide.
- The dataset covers remote listings classified as worldwide-friendly by the provider.
- Some listings may have additional requirements or restrictions.
- Exact career-title matching may exclude relevant job titles with different wording.
- Some matching job titles may represent specialized or senior roles rather than entry-level opportunities.
- A zero matching count does not demonstrate zero market demand.
- The counts are not directly comparable measures of occupational demand because the search queries have different coverage.
- A single observation cannot establish whether a career is rising, stable or declining.
- Job listings may expire or close after collection.

FuturePath AI must present these observations as source-specific market signals rather than guaranteed employment opportunities.

## 5. Future Improvements

Possible improvements include:

- Support additional job-title aliases, such as `Cyber Security Analyst`, `SOC Analyst` and `Software Engineer`.
- Collect comparable daily observations to support historical analysis.
- Verify whether individual listings are still active.
- Add independent labour-market forecasts from published research.
- Improve geographical relevance for different users.
- Regularly review source availability, accuracy and usage conditions.

## 6. Attribution and Responsible Use

Job-market data is sourced from Himalayas.

Website: https://himalayas.app

API Terms: https://himalayas.app/terms

FuturePath AI will provide visible attribution when displaying Himalayas-derived information and use the provider's application links where individual job listings are shown.

The project will not present search-result counts as official employment statistics or independently verified future forecasts.