from __future__ import annotations

from backend.matching import load_role_skills, load_trend_signals, match_roles
from frontend.studio import render_studio
import streamlit as st

st.set_page_config(
    page_title="FuturePath AI | Career Readiness",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROLES = [
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "Cybersecurity Analyst",
    "Cloud Engineer",
    "Software Developer",
]
INTERESTS = ["Data", "AI", "Cybersecurity", "Cloud", "Software Development"]
DEGREES = [
    "Computer Science",
    "Information and Communication Technology (ICT)",
    "Software Engineering",
    "Data Science",
    "Cybersecurity",
    "Information Systems",
    "Other / Still studying",
]

# The team's source data is left unchanged. These aliases make common spelling
# and role-name variants line up with the interface and its learning catalog.
ROLE_ALIASES = {"Software Engineer": "Software Developer"}
SKILL_ALIASES = {
    "amazon web services": "AWS",
    "microsoft azure": "Azure",
    "microsoft excel": "Excel",
    "microsoft power bi": "Power BI",
    "powershell": "PowerShell",
    "tensor flow": "TensorFlow",
}

ROLE_INTERESTS = {
    "Data Analyst": {"Data"},
    "Data Scientist": {"Data", "AI"},
    "Machine Learning Engineer": {"AI", "Software Development"},
    "Cybersecurity Analyst": {"Cybersecurity"},
    "Cloud Engineer": {"Cloud"},
    "Software Developer": {"Software Development"},
}

LEARNING_RESOURCES = {
    "Python": {
        "provider": "Kaggle Learn",
        "title": "Python",
        "url": "https://www.kaggle.com/learn/python",
        "duration": "5 hours",
    },
    "SQL": {
        "provider": "Kaggle Learn",
        "title": "Intro to SQL",
        "url": "https://www.kaggle.com/learn/intro-to-sql",
        "duration": "3 hours",
    },
    "Excel": {
        "provider": "GCFGlobal / LearnFree",
        "title": "Excel tutorials",
        "url": "https://edu.gcfglobal.org/en/excel/",
    },
    "R": {
        "provider": "Posit Cloud Education",
        "title": "Primers: interactive R lessons",
        "url": "https://posit.cloud/learn/primers",
    },
    "Tableau": {
        "provider": "Tableau",
        "title": "Free Training Videos",
        "url": "https://www.tableau.com/learn/training",
    },
    "Power BI": {
        "provider": "Microsoft Learn",
        "title": "Power BI learning paths",
        "url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/",
    },
    "TensorFlow": {
        "provider": "TensorFlow",
        "title": "TensorFlow tutorials",
        "url": "https://www.tensorflow.org/tutorials",
    },
    "PyTorch": {
        "provider": "PyTorch",
        "title": "Learn the Basics",
        "url": "https://pytorch.org/tutorials/beginner/basics/intro.html",
    },
    "MLOps": {
        "provider": "Made With ML",
        "title": "MLOps Course",
        "url": "https://madewithml.com/courses/mlops",
    },
    "Docker": {
        "provider": "Docker",
        "title": "Docker Get Started",
        "url": "https://docs.docker.com/get-started/",
    },
    "Kubernetes": {
        "provider": "Kubernetes",
        "title": "Learn Kubernetes Basics",
        "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
    },
    "Linux": {
        "provider": "Linux Journey",
        "title": "Learn Linux",
        "url": "https://linuxjourney.com/",
    },
    "Azure": {
        "provider": "Microsoft Learn",
        "title": "Azure training",
        "url": "https://learn.microsoft.com/en-us/training/azure/",
    },
    "PowerShell": {
        "provider": "Microsoft Learn",
        "title": "PowerShell learning paths",
        "url": "https://learn.microsoft.com/en-us/training/browse/?products=powershell",
    },
    "AWS": {
        "provider": "AWS Skill Builder",
        "title": "AWS Cloud Practitioner Essentials",
        "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials",
    },
    "Java": {
        "provider": "dev.java",
        "title": "Learn Java",
        "url": "https://dev.java/learn/",
    },
    "JavaScript": {
        "provider": "MDN Web Docs",
        "title": "JavaScript guide",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
    },
    "Git": {
        "provider": "Pro Git",
        "title": "Read the Pro Git book online",
        "url": "https://git-scm.com/book/en/v2",
    },
    "Splunk Enterprise": {
        "provider": "Splunk",
        "title": "Splunk Education",
        "url": "https://www.splunk.com/en_us/training.html",
    },
}
LOW_COST_COURSES = {
    "SQL": {
        "provider": "Udemy",
        "title": "The Ultimate MySQL Bootcamp: Go from SQL Beginner to Expert",
        "url": "https://www.udemy.com/course/the-ultimate-mysql-bootcamp-go-from-sql-beginner-to-expert/",
        "price": 10.99,
        "currency": "USD",
        "checked_on": "21 Oct 2026",
    },
}
PERSONAS = {
    "cs_student": {
        "name": "Student Preview",
        "degree": "Computer Science",
        "skills": ["Python", "SQL", "Git"],
        "interests": ["Data", "AI"],
    },
    "qa_analyst": {
        "name": "Student Preview",
        "degree": "Information and Communication Technology (ICT)",
        "skills": ["SQL", "Git", "Excel"],
        "interests": ["Software Development", "Data"],
    },
    "web_dev": {
        "name": "Student Preview",
        "degree": "Software Engineering",
        "skills": ["JavaScript", "Git", "Docker"],
        "interests": ["Software Development", "Cloud"],
    },
}
FALLBACK_SKILLS = [
    "Python", "SQL", "Excel", "Git", "Linux", "Statistics",
    "Machine Learning", "AWS", "Azure", "PowerShell", "Java",
    "JavaScript", "Power BI", "Docker", "Kubernetes",
]


def canonical_role(role: str) -> str:
    return ROLE_ALIASES.get(role.strip(), role.strip())


def canonical_skill(skill: str) -> str:
    value = skill.strip()
    return SKILL_ALIASES.get(value.casefold(), value)


def get_weighted_benchmarks() -> dict[str, dict[str, float]]:
    """Load team weights, normalizing display aliases without editing the CSV."""
    weighted: dict[str, dict[str, float]] = {}
    for source_role, skills in load_role_skills().items():
        role = canonical_role(source_role)
        role_skills = weighted.setdefault(role, {})
        for source_skill, weight in skills.items():
            skill = canonical_skill(source_skill)
            # Aliases that describe the same skill should not count twice.
            numeric_weight = float(weight)
            role_skills.setdefault(
                skill,
                int(numeric_weight) if numeric_weight.is_integer() else numeric_weight,
            )
    return weighted


def get_market_data() -> dict[str, dict]:
    return {
        canonical_role(role): signal
        for role, signal in load_trend_signals().items()
    }


def get_trend_rows(market_data: dict[str, dict]) -> list[dict]:
    rows = []
    for role in ROLES:
        signal = market_data.get(role)
        if not signal:
            continue
        rows.append({
            "role": role,
            "value": signal["market_listing_count"],
            "source_url": signal["market_source_url"],
            "retrieved_at": signal["retrieved_at"],
        })
    return rows


role_weights = get_weighted_benchmarks()
if not role_weights:
    # Keep the interface usable if the team CSV is temporarily empty, while
    # clearly marking those built-in examples as illustrative.
    role_weights = {
        "Data Analyst": {"SQL": 1, "Excel": 1, "Python": 1},
        "Data Scientist": {"Python": 1, "SQL": 1, "TensorFlow": 1},
        "Machine Learning Engineer": {"Python": 1, "PyTorch": 1, "MLOps": 1},
        "Cybersecurity Analyst": {"Linux": 1, "Python": 1, "Splunk Enterprise": 1},
        "Cloud Engineer": {"Linux": 1, "Azure": 1, "Docker": 1},
        "Software Developer": {"Java": 1, "JavaScript": 1, "Git": 1},
    }
    benchmark_is_illustrative = True
else:
    benchmark_is_illustrative = False

roles = [role for role in ROLES if role in role_weights]
benchmarks = {role: list(skills) for role, skills in role_weights.items()}
benchmark_weights = role_weights
market_data = get_market_data()
trend_rows = get_trend_rows(market_data)
trend_date = max(
    (row["retrieved_at"] or "" for row in trend_rows),
    default="No data loaded",
)
trend_error = None if trend_rows else "Job-market snapshot data is not available yet."

all_skills = {
    canonical_skill(skill)
    for role_skills in role_weights.values()
    for skill in role_skills
}
all_skills.update(FALLBACK_SKILLS)
all_skills.update(
    skill
    for persona in PERSONAS.values()
    for skill in persona["skills"]
)

backend_order = {}
for persona_key, profile in PERSONAS.items():
    normalized_user_skills = [canonical_skill(skill) for skill in profile["skills"]]
    ranked = match_roles(normalized_user_skills, role_weights, market_data)
    backend_order[persona_key] = [item["role"] for item in ranked]

render_studio({
    "roles": roles,
    "interests": INTERESTS,
    "degrees": DEGREES,
    "benchmarks": benchmarks,
    "benchmarkWeights": benchmark_weights,
    "roleInterests": {
        role: sorted(ROLE_INTERESTS.get(role, set()))
        for role in roles
    },
    "resources": LEARNING_RESOURCES,
    "lowCost": LOW_COST_COURSES,
    "skills": sorted(all_skills),
    "benchmarkIsIllustrative": benchmark_is_illustrative,
    "trendRows": trend_rows,
    "trendError": trend_error,
    "trendDate": trend_date,
    "source": "Himalayas Remote Jobs API",
    "personas": PERSONAS,
    "backendOrder": backend_order,
})