## Job-Market Data Collection

### Data Source
Himalayas Remote Jobs API

### Collection Process
1. Search for each of the six career roles.
2. Apply the worldwide remote-job filter.
3. Retrieve all available search-result pages.
4. Filter listings using the career phrase in the job title.
5. Remove duplicate listings using unique job identifiers.
6. Record the count, source URL and collection date.

### Metric
title_matched_unique_remote_listings

This metric represents unique, title-matching remote job
listings found in the Himalayas API search results.

It does not represent total worldwide employment demand.

### Limitations
- Only covers listings indexed by Himalayas.
- May miss related job titles and synonyms.
- Worldwide-filtered listings are not necessarily suitable
  for every applicant.
- Different search terms have different coverage.
- One snapshot cannot establish rising or declining trends.
- The counts are not directly comparable measures of
  demand across different occupations.

### Future Improvements
- Add validated job-title aliases.
- Collect comparable observations over time.
- Add independent longer-term labour-market forecasts.