import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ROLE_SKILLS_FILE = DATA_DIR / "role_skills.csv"


def load_role_skills(path=ROLE_SKILLS_FILE):
    """Read role_skills.csv into {role: {skill: weight}}.

    Returns an empty dict if the file is missing or has no data rows.
    Rows with a blank role/skill or a non-positive or non-numeric
    weight are skipped.
    """
    path = Path(path)

    if not path.exists() or path.stat().st_size == 0:
        return {}

    roles = {}

    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            role = (row.get("role") or "").strip()
            skill = (row.get("skill") or "").strip()

            try:
                weight = float(row.get("weight") or "")
            except ValueError:
                continue

            if not role or not skill or weight <= 0:
                continue

            roles.setdefault(role, {})[skill] = weight

    return roles
