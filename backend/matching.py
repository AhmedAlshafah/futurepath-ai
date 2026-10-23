import csv
from pathlib import Path

# Folder that holds our CSV files: go up one level from backend/ to the project root, then into data/.
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# Full path to the file that lists which skills each role needs (and how important each one is).
ROLE_SKILLS_FILE = DATA_DIR / "role_skills.csv"

# Full path to the file with job market numbers for each role (collected by script/collect_trends.py).
TREND_SIGNALS_FILE = DATA_DIR / "trend_signals.csv"

# The only metric we currently read from trend_signals.csv: how many unique remote job listings
# had a title matching the role. Rows with any other metric are ignored.
MARKET_METRIC = "title_matched_unique_remote_listings"

# Different spellings that mean the same skill. Keys and values are lowercase.
# The left side is a short/alternate name, the right side is the name used in role_skills.csv.
SKILL_ALIASES = {
    "excel": "microsoft excel",
    "power bi": "microsoft power bi",
    # role_skills.csv spells this both ways ("Tensor Flow" and "TensorFlow"), so treat them as one.
    "tensor flow": "tensorflow",
}


def normalize_skill(name):
    """Turn a skill name into one comparable key, e.g. " Excel " -> "microsoft excel"."""
    # Lowercase it, and split()/join() trims the ends and squashes repeated spaces into one.
    key = " ".join(name.lower().split())

    # If this spelling has an alias, swap in the official name; otherwise keep it as is.
    return SKILL_ALIASES.get(key, key)


def load_role_skills(path=ROLE_SKILLS_FILE):
    """Read role_skills.csv into {role: {skill: weight}}.

    Returns an empty dict if the file is missing or has no data rows.
    Rows with a blank role/skill or a non-positive or non-numeric
    weight are skipped.
    """
    # Turn the path into a Path object so it works whether we were given a string or a Path.
    path = Path(path)

    # If the file doesn't exist or is completely empty, there's no data, so return an empty dict.
    if not path.exists() or path.stat().st_size == 0:
        return {}

    # This will end up looking like {"Data Analyst": {"SQL": 3.0, "Excel": 2.0}, ...}.
    roles = {}

    # Open the CSV. newline="" is what the csv module expects; utf-8 handles special characters.
    with open(path, newline="", encoding="utf-8") as f:
        # DictReader gives each row as a dict keyed by the header, e.g. row["role"].
        for row in csv.DictReader(f):
            # Read the role and skill, treating a missing value as "" and trimming extra spaces.
            role = (row.get("role") or "").strip()
            skill = (row.get("skill") or "").strip()

            # Convert the weight text to a number. If it isn't a number (or is blank), skip the row.
            try:
                weight = float(row.get("weight") or "")
            except ValueError:
                continue

            # Skip rows with no role, no skill, or a weight of 0 or less (they can't count toward a score).
            if not role or not skill or weight <= 0:
                continue

            # Create the role's inner dict the first time we see the role, then store the skill's weight.
            roles.setdefault(role, {})[skill] = weight

    # Hand back the finished {role: {skill: weight}} dict.
    return roles


def load_trend_signals(path=TREND_SIGNALS_FILE):
    """Read trend_signals.csv into {role: market info} for MARKET_METRIC.

    Each value is a dict with market_listing_count, market_metric,
    market_source_url and retrieved_at. If a role has several rows,
    the most recent retrieved_at wins. Returns an empty dict if the
    file is missing or has no usable rows.
    """
    # Same as above: accept a string or a Path.
    path = Path(path)

    # No file or an empty file means no market data.
    if not path.exists() or path.stat().st_size == 0:
        return {}

    # This will end up looking like {"Data Analyst": {"market_listing_count": 12, ...}, ...}.
    signals = {}

    # Open and read the CSV row by row, the same way as load_role_skills.
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            # Read and tidy the fields we need.
            role = (row.get("role") or "").strip()
            metric = (row.get("metric") or "").strip()
            retrieved_at = (row.get("retrieved_at") or "").strip()

            # Only keep rows that have a role and use the metric we understand.
            if not role or metric != MARKET_METRIC:
                continue

            # The listing count must be a whole number. If it isn't, skip the row.
            try:
                count = int(row.get("value") or "")
            except ValueError:
                continue

            # If we already have a newer row for this role, keep that one and skip this older row.
            # Dates are stored as YYYY-MM-DD, so comparing them as text sorts them correctly.
            existing = signals.get(role)
            if existing and existing["retrieved_at"] > retrieved_at:
                continue

            # Store this row's market info for the role.
            signals[role] = {
                "market_listing_count": count,
                "market_metric": metric,
                "market_source_url": (row.get("source_url") or "").strip() or None,
                "retrieved_at": retrieved_at or None,
            }

    # Hand back the finished {role: market info} dict.
    return signals


def match_roles(user_skills, role_skills, trend_signals=None):
    """Score each role by how much of its weighted skill set the user has.

    Skill names on both sides go through normalize_skill, so "Excel" matches
    "Microsoft Excel". Only skills are scored (interests are unused in the MVP).

    Returns every role as a list of dicts sorted best match first. Each dict has:
      role, match_pct (0-100, weighted), matched_skills, missing_skills,
      market_listing_count, market_metric, market_source_url, retrieved_at
      (all None when the role has no market data), trend_score (always None)
      and trend (always "Unknown").
    """
    # If no market data was passed in, use an empty dict so every role just gets None market fields.
    trend_signals = trend_signals or {}

    # Normalize the user's skills so "python ", "Python" and "Excel"/"Microsoft Excel" compare equal.
    # A set makes the "does the user have this skill?" check fast.
    user = {normalize_skill(s) for s in user_skills if s and s.strip()}

    # This list collects one result per role.
    results = []

    # Go through every role and its {skill: weight} dictionary.
    for role, skills in role_skills.items():
        # Add up all the weights for the role. This is the most a user could score.
        total = sum(skills.values())

        # A role with no weights can't be scored (and dividing by 0 would crash), so skip it.
        if total <= 0:
            continue

        # Skills the role needs that the user already has. The dataset name is normalized
        # the same way as the user's, but we keep the dataset's spelling for display.
        matched = [skill for skill in skills if normalize_skill(skill) in user]

        # Skills the role needs that the user doesn't have yet (their skill gap).
        missing = [skill for skill in skills if normalize_skill(skill) not in user]

        # Add up the weights of the matched skills only.
        earned = sum(skills[skill] for skill in matched)

        # Look up this role's market info. If there is none, use {} so .get() below returns None.
        market = trend_signals.get(role, {})

        # Build the result in the agreed contract shape.
        results.append({
            "role": role,
            # Weighted share of the role's skills the user covers, as a percentage (e.g. 71.4).
            "match_pct": round(earned / total * 100, 1),
            "matched_skills": matched,
            "missing_skills": missing,
            # Job market numbers from trend_signals.csv (None if this role isn't in that file).
            "market_listing_count": market.get("market_listing_count"),
            "market_metric": market.get("market_metric"),
            "market_source_url": market.get("market_source_url"),
            "retrieved_at": market.get("retrieved_at"),
            # We don't have enough history to calculate a trend yet, so these are fixed placeholders.
            "trend_score": None,
            "trend": "Unknown",
        })

    # Sort best match first. If two roles tie, sort them alphabetically so the order is always the same.
    results.sort(key=lambda r: (-r["match_pct"], r["role"]))

    # Return the ranked list.
    return results
