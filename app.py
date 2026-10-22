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
def canonical_role(role: str) -> str:
    return ROLE_ALIASES.get(role.strip(), role.strip())


def canonical_skill(skill: str) -> str:
    value = skill.strip()
    return SKILL_ALIASES.get(value.casefold(), value)


def get_weighted_benchmarks(source_weights) -> dict[str, dict[str, float]]:
    """Create presentation labels only; this mapping is never used for scoring."""
    weighted: dict[str, dict[str, float]] = {}
    for source_role, skills in source_weights.items():
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


def get_role_options(weighted_benchmarks) -> list[str]:
    """Keep role selectors and market rows aligned with CSV-backed benchmarks."""
    return sorted(weighted_benchmarks, key=str.casefold)


def get_skill_options(weighted_benchmarks) -> list[str]:
    """Expose each unique benchmark skill as a selectable frontend option."""
    return sorted(
        {
            skill
            for role_skills in weighted_benchmarks.values()
            for skill in role_skills
        },
        key=str.casefold,
    )


def get_market_data(source_signals) -> dict[str, dict]:
    return {
        canonical_role(role): signal
        for role, signal in source_signals.items()
    }


def get_trend_rows(
    market_data: dict[str, dict], available_roles: list[str]
) -> list[dict]:
    rows = []
    for role in available_roles:
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


source_role_weights = load_role_skills()
source_market_data = load_trend_signals()
# Form labels may be shorter, but their submitted values retain CSV spelling.
skill_values = {
    canonical_skill(skill): skill
    for skills in source_role_weights.values()
    for skill in skills
}
role_weights = get_weighted_benchmarks(source_role_weights)
benchmark_is_illustrative = False

roles = get_role_options(role_weights)
benchmarks = {role: list(skills) for role, skills in role_weights.items()}
benchmark_weights = role_weights
market_data = get_market_data(source_market_data)
trend_rows = get_trend_rows(market_data, roles)
trend_date = max(
    (row["retrieved_at"] or "" for row in trend_rows),
    default="No data loaded",
)
trend_error = None if trend_rows else "Job-market snapshot data is not available yet."

all_skills = set(get_skill_options(role_weights))

def backend_matches_for(user_skills: list[str]) -> list[dict]:
    """Use the team's matcher as the sole source for visible scores and ordering."""
    if not source_role_weights or not user_skills:
        return []
    # Pass the original team data unchanged. Aliases below affect labels only.
    matches = match_roles(user_skills, source_role_weights, source_market_data)
    return [
        {
            **result,
            "role": canonical_role(result["role"]),
            "matched_skills": [
                canonical_skill(skill) for skill in result["matched_skills"]
            ],
            "missing_skills": [
                canonical_skill(skill) for skill in result["missing_skills"]
            ],
        }
        for result in matches
    ]


def _clean_component_value(value):
    """Validate the browser component's profile and view state before storing it."""
    if not isinstance(value, dict):
        return None

    profile = value.get("profile")
    ui_state = value.get("uiState")
    if not isinstance(profile, dict) or not isinstance(ui_state, dict):
        return None

    known_degrees = set(DEGREES)
    known_interests = set(INTERESTS)
    known_personas = set(PERSONAS)
    known_roles = set(roles)
    known_pages = {
        "page-market",
        "page-profile",
        "page-matches",
        "page-reskilling",
    }

    def clean_text_list(items, *, limit=100, max_length=80):
        if not isinstance(items, list):
            return []
        cleaned = []
        seen = set()
        for item in items[:limit]:
            if not isinstance(item, str):
                continue
            text = item.strip()[:max_length]
            key = text.casefold()
            if text and key not in seen:
                seen.add(key)
                cleaned.append(text)
        return cleaned

    persona = profile.get("persona")
    persona = persona if persona in known_personas else None
    degree = profile.get("degree")
    degree = degree if degree in known_degrees else DEGREES[0]
    selected_role = ui_state.get("selectedRole")
    selected_role = selected_role if selected_role in known_roles else None
    page = ui_state.get("page")
    page = page if page in known_pages else "page-market"

    tiers = profile.get("tiers")
    if not isinstance(tiers, dict):
        tiers = {}
    tiers = {
        str(skill)[:80]: level
        for skill, level in list(tiers.items())[:100]
        if isinstance(skill, str)
        and level in {"Beginner", "Intermediate", "Advanced"}
    }

    completed = ui_state.get("completed")
    if not isinstance(completed, dict):
        completed = {}
    completed = {
        str(key)[:160]: bool(done)
        for key, done in list(completed.items())[:200]
        if isinstance(key, str)
    }

    runway = ui_state.get("runway")
    runway = runway if runway in {4, 8, 12} else 8
    budget = ui_state.get("budget")
    budget = budget if budget in {"free", "lowcost"} else "free"
    pace = ui_state.get("pace")
    pace = pace if pace in {"steady", "focused"} else "steady"

    return {
        "profile": {
            "name": str(profile.get("name") or "Student Preview")[:60],
            "degree": degree,
            "skills": clean_text_list(profile.get("skills")),
            "interests": [
                item for item in clean_text_list(profile.get("interests"))
                if item in known_interests
            ],
            "persona": persona,
            "custom": clean_text_list(profile.get("custom")),
            "tiers": tiers,
        },
        "uiState": {
            "page": page,
            "selectedRole": selected_role,
            "runway": runway,
            "budget": budget,
            "pace": pace,
            "completed": completed,
            "cvFound": clean_text_list(ui_state.get("cvFound")),
        },
    }


if "futurepath_profile" not in st.session_state:
    st.session_state.futurepath_profile = {
        **PERSONAS["cs_student"],
        "persona": "cs_student",
        "custom": [],
        "tiers": {},
    }
if "futurepath_ui_state" not in st.session_state:
    st.session_state.futurepath_ui_state = {
        "page": "page-market",
        "selectedRole": None,
        "runway": 8,
        "budget": "free",
        "pace": "steady",
        "completed": {},
        "cvFound": [],
    }

profile = st.session_state.futurepath_profile
ui_state = st.session_state.futurepath_ui_state
backend_matches = backend_matches_for(profile["skills"])
match_error = (
    "No role data yet. Add rows to data/role_skills.csv."
    if not source_role_weights else
    "Select at least one skill to see your matches."
    if not profile["skills"] else None
)

component_value = render_studio({
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
    "skillValues": skill_values,
    "benchmarkIsIllustrative": benchmark_is_illustrative,
    "trendRows": trend_rows,
    "trendError": trend_error,
    "trendDate": trend_date,
    "source": "Himalayas Remote Jobs API",
    "personas": PERSONAS,
    "profile": {
        **profile,
        "skills": [canonical_skill(skill) for skill in profile["skills"]],
    },
    "uiState": ui_state,
    "backendMatches": backend_matches,
    "matchError": match_error,
    "scoreSource": "backend.match_roles",
})

cleaned = _clean_component_value(component_value)
if cleaned and (
    cleaned["profile"] != profile or cleaned["uiState"] != ui_state
):
    st.session_state.futurepath_profile = cleaned["profile"]
    st.session_state.futurepath_ui_state = cleaned["uiState"]
    st.rerun()
