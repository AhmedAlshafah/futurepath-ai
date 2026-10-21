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


def match_roles(user_skills, role_skills):
    """Score each role by how much of its weighted skill set the user has.

    Returns a list of dicts sorted best match first, each with the role,
    a score from 0 to 1, and the matched and missing skills.
    """
    # Lowercase and trim the user's skills so "python " and "Python" count as the same skill.
    # A set makes the "does the user have this skill?" check fast.
    user = {s.strip().lower() for s in user_skills if s and s.strip()}

    # This list collects one result per role.
    results = []

    # Go through every role and its {skill: weight} dictionary.
    for role, skills in role_skills.items():
        # Add up all the weights for the role. This is the most a user could score.
        total = sum(skills.values())

        # A role with no weights can't be scored (and dividing by 0 would crash), so skip it.
        if total <= 0:
            continue

        # Skills the role needs that the user already has.
        matched = [skill for skill in skills if skill.lower() in user]

        # Skills the role needs that the user doesn't have yet (their skill gap).
        missing = [skill for skill in skills if skill.lower() not in user]

        # Add up the weights of the matched skills only.
        earned = sum(skills[skill] for skill in matched)

        # Save the result. Score = share of the role's total weight the user covers, from 0 to 1.
        results.append({
            "role": role,
            "score": round(earned / total, 3),
            "matched": matched,
            "missing": missing,
        })

    # Sort best match first. If two scores tie, sort those roles alphabetically so the order is always the same.
    results.sort(key=lambda r: (-r["score"], r["role"]))

    # Return the ranked list.
    return results
