# FuturePath AI

**SDC Hackathon 2026 — Domain 1: Aiversecity, Future-Ready Workforce**

FuturePath AI is an explainable career guidance platform that helps students and fresh graduates identify suitable technology careers, understand their skill gaps, and build practical learning plans.

## 1. Team Information

| Field                  | Details                                                            |
| ---------------------- | ------------------------------------------------------------------ |
| Team Name              | NovaMind                                                           |
| Domain                 | Domain 1 — Aiversecity: Future-Ready Workforce                     |
| SDG Track              | SDG 4 — Quality Education; SDG 8 — Decent Work and Economic Growth |
| Registered Team Leader | Christopher                                                        |
| University             | Asia Pacific University (APU) — verify member affiliations         |
| Number of Members      | 5                                                                  |

### Team Members

| Name                 | Responsibility                             |
| -------------------- | ------------------------------------------ |
| Ahmed                | Team/Product Lead, Data and Research       |
| Aung Ko Htwe (Keran) | Backend Development and Matching Algorithm |
| Yap Tian Hong        | Career Skills and Data Research            |
| Christopher          | Frontend, Streamlit UI and Replit          |
| Sunny Yang           | Pitch, Documentation and Testing           |

## 2. Important Links

| Resource          | Link                                                                                             |
| ----------------- | ------------------------------------------------------------------------------------------------ |
| GitHub Repository | [https://github.com/AhmedAlshafah/futurepath-ai](https://github.com/AhmedAlshafah/futurepath-ai) |
| Live Application  | [https://futurepath-ai.replit.app/](https://futurepath-ai.replit.app/)                           |
| Replit Project    | https://replit.com/t/sdc-hackathon/repls/futurepath-ai                                                       |
| Pitch Slides      | [Add final accessible link]                                                                      |
| Demo Video        | [Add final accessible link]                                                                      |

## 3. Problem Statement

The rapid development of artificial intelligence is changing the skills required in the technology workforce. University students and fresh graduates may struggle to identify suitable careers, understand which skills employers seek, and decide what to learn next.

FuturePath AI aims to make career exploration and reskilling decisions clearer by connecting users' existing skills with researched career benchmarks and dated job-market information.

## 4. Our Solution

FuturePath AI compares a user's selected skills with the skill requirements of six supported technology careers.

The platform uses a transparent, Python-based weighted skill-matching algorithm to calculate career alignment percentages.

Users can explore their career matches, inspect missing skills, review learning resources, and export learning plans.

## 5. Key Features

- **User Profile:** Users select their current skills and interests.
- **Career Matching:** Six technology roles are ranked using weighted skill alignment.
- **Explainable Results:** Shows matching percentages, matched skills and missing skills.
- **Job-Market Snapshot:** Displays dated observations collected using the Himalayas Remote Jobs API.
- **Reskilling Plans:** Provides recommended skills and learning resources.
- **Export Options:** Supports downloading learning plans in available formats, including PDF, Markdown and calendar files.

### Supported Career Roles

1. Data Analyst
2. Data Scientist
3. Machine Learning Engineer
4. Cybersecurity Analyst
5. Cloud Engineer
6. Software Developer

## 6. Technology Stack

| Component             | Technology                                |
| --------------------- | ----------------------------------------- |
| Programming Language  | Python                                    |
| Application Framework | Streamlit                                 |
| Frontend              | HTML, CSS and JavaScript                  |
| Matching System       | Python weighted skill-alignment algorithm |
| Research Data         | O\*NET and supplementary career sources   |
| Job-Market Data       | Himalayas Remote Jobs API                 |
| Data Storage          | CSV files                                 |
| Hosting               | Replit                                    |
| Version Control       | Git and GitHub                            |

The current matching system is deterministic. Generative-AI development tools supported the implementation process, but an LLM is not required to calculate career-match percentages.

## 7. Project Structure

```text
futurepath-ai/
├── .streamlit/
├── backend/
│   ├── __init__.py
│   └── matching.py
├── data/
│   ├── role_skills.csv
│   └── trend_signals.csv
├── docs/
│   ├── data_research.md
│   ├── data_sources.md
│   └── methodology.md
├── frontend/
├── script/
│   ├── check_himalayas.py
│   └── collect_trends.py
├── submission/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## 8. How to Run FuturePath AI

### Option 1 — Use the Live Application

The easiest way to test FuturePath AI is through our deployed application:

[https://futurepath-ai.replit.app/](https://futurepath-ai.replit.app/)

No local installation is required.

**Demo instructions:**

1. Open the application.
2. Start your career exploration.
3. Select your existing skills, for example Python and SQL.
4. View the ranked career results.
5. Select a career to examine skill gaps.
6. Open the suggested learning plan.
7. Review the job-market snapshot and available export options.

### Option 2 — Run Locally

**Requirements:**

- Python 3
- Git
- Internet access for installation

**Step 1: Clone the repository**

```bash
git clone https://github.com/AhmedAlshafah/futurepath-ai.git
cd futurepath-ai
```

**Step 2: Create a virtual environment**

```bash
python3 -m venv .venv
```

**Step 3: Activate the environment**

For macOS or Linux:

```bash
source .venv/bin/activate
```

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

**Step 4: Install dependencies**

```bash
python -m pip install -r requirements.txt
```

**Step 5: Start the application**

```bash
python -m streamlit run app.py
```

**Step 6: Open the local application**

Navigate to:

[http://localhost:8501](http://localhost:8501)

The application reads the included CSV files. A live Himalayas API connection is not required to use the included dated job-market snapshot.

## 9. Matching Methodology

Each career has a list of skills, with weights representing their relative importance within the team's benchmark.

The skill alignment percentage is calculated as:

**Skill Alignment (%) = (Total weight of matched skills / Total weight of all role skills) × 100**

For example, when a user selects Python and SQL, the approved dataset produces a Data Scientist skill alignment of approximately 42.9%.

The matching percentage is not an employment probability, certification of competence or prediction of hiring success.

## 10. Data Sources

### Career Skills

- O\*NET OnLine: [https://www.onetonline.org/](https://www.onetonline.org/)
- Supplementary research sources documented in `docs/data_research.md` and `docs/data_sources.md`

### Job-Market Information

- Himalayas Remote Jobs API: [https://himalayas.app/jobs/api](https://himalayas.app/jobs/api)

The current job-market snapshot was collected on 21 October 2026. It reflects a limited set of remote job listings observed at that time and is not a comprehensive forecast of labor-market demand.

## 11. How We Used Replit

Replit was used to test, run and deploy FuturePath AI as a browser-accessible application.

The deployed Streamlit application provides the user interface and connects to the Python matching system and project datasets.

The live prototype is available through the link provided in Section 2.

Replit proof-of-use evidence is included in the `submission/` folder.

## 12. Testing

The team performed functional testing of the career matching and application workflow.

Example acceptance cases include:

| Selected Skills    | Expected Result                            |
| ------------------ | ------------------------------------------ |
| Python + Excel     | Data Analyst: 33.3%                        |
| Python + SQL       | Data Scientist: 42.9%; Data Analyst: 41.7% |
| No selected skills | User receives a validation message         |

Additional checks cover career-role mappings, skill-gap explanations, learning-plan navigation, file exports and the public deployment.

These expectations are based on the team's approved skill-weight dataset.

## 13. Known Limitations

- The prototype supports six technology careers.
- Skill weights are team-defined research benchmarks.
- Job-market observations are limited to a dated remote-job snapshot.
- Skill selection does not independently verify user proficiency.
- Interests do not currently contribute to the weighted skill-alignment score.
- Career rankings do not predict hiring outcomes.

## 14. Future Improvements

- Broader career and industry coverage
- Regularly updated job-market datasets
- Improved CV skill extraction
- More advanced personalized recommendations
- Expanded reskilling pathways
- User testing and validation of career guidance quality

## 15. Sustainable Development Goals

FuturePath AI primarily supports:

**SDG 4 — Quality Education:** Helping students identify employment-relevant technical skills and learning opportunities.

**SDG 8 — Decent Work and Economic Growth:** Supporting career preparation and awareness of changing workforce skill requirements.

## 16. Submission Documents

The `submission/` folder contains the preliminary proposal, technical and tools declaration, and applicable proof-of-use documentation required for the hackathon.

The pitch video and presentation slides are linked in Section 2.

## 17. License

The project is distributed under the Apache License 2.0, as specified in the repository's `LICENSE` file. Third-party datasets, libraries and other materials remain subject to their own applicable licenses and terms.
