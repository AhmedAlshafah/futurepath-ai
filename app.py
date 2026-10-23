import streamlit as st

# Bring in the backend functions: two load the CSVs, the other scores roles.
from backend.matching import load_role_skills, load_trend_signals, match_roles

# How many roles to show as the main results; the rest go in the "Other roles" section.
TOP_N = 3


def show_role(r):
    """Draw one role's result: name, Skill Alignment bar, skills and market info."""
    # Role name with its Skill Alignment, e.g. "Data Analyst — Skill Alignment: 33.3%".
    st.markdown(f"**{r['role']}** — Skill Alignment: {r['match_pct']:.1f}%")

    # A progress bar. st.progress wants 0 to 1, so divide the percentage by 100.
    st.progress(r["match_pct"] / 100)

    # List the skills the user already has for this role, if any.
    if r["matched_skills"]:
        st.write("✅ You have: " + ", ".join(r["matched_skills"]))

    # List the skills the user still needs to learn, if any.
    if r["missing_skills"]:
        st.write("📚 To learn: " + ", ".join(r["missing_skills"]))

    # Show the job market count only if we have one for this role (0 is a real value, so check for None).
    if r["market_listing_count"] is not None:
        # The stored source is the Himalayas API link, which shows raw JSON text in a browser.
        # Dropping "/api/search" turns it into the normal search page with readable job listings.
        jobs_url = (r["market_source_url"] or "").replace("/jobs/api/search", "/jobs")

        st.caption(
            f"💼 {r['market_listing_count']} remote listings found "
            f"(as of {r['retrieved_at']}) · [view jobs]({jobs_url})"
        )


st.set_page_config(
    page_title="FuturePath AI",
    page_icon="🎯"
)

st.title("FuturePath AI")
st.write("AI-powered future career guidance")

st.subheader("Your Profile")

name = st.text_input("Your name")

skills = st.multiselect(
    "Select your current skills",
    ["Python", "SQL", "Excel", "Power BI", "Machine Learning", "Cloud Computing"]
)

# NOTE: interests are collected but unused in the MVP — they do not affect the score.
interests = st.multiselect(
    "Select your interests",
    ["Data", "AI", "Cybersecurity", "Cloud", "Software Development"]
)

if st.button("Find My Future Careers"):
    # Load the {role: {skill: weight}} data from data/role_skills.csv.
    role_skills = load_role_skills()

    # If the CSV has no rows yet, there is nothing to match against, so say so.
    if not role_skills:
        st.warning("No role data yet. Add rows to data/role_skills.csv.")

    # If the user didn't pick any skills, ask them to.
    elif not skills:
        st.info("Select at least one skill to see your matches.")

    # Otherwise, score every role and show the results.
    else:
        # Load the job market numbers from data/trend_signals.csv.
        trend_signals = load_trend_signals()

        # Rank all roles against the user's selected skills (best match first).
        # match_roles normalizes skill names itself, so "Excel" matches "Microsoft Excel".
        results = match_roles(skills, role_skills, trend_signals)

        st.subheader("Your Career Matches")

        # Be clear about what the number means: skills only, not overall career suitability.
        st.caption("Skill Alignment = how much of each role's weighted skill set you already have. "
                   "Interests are not scored yet.")

        # The top 3 roles are the main results, shown directly on the page.
        for r in results[:TOP_N]:
            show_role(r)

        # Every other role goes inside a collapsible section so the page stays short.
        others = results[TOP_N:]
        if others:
            with st.expander("Other roles"):
                for r in others:
                    show_role(r)