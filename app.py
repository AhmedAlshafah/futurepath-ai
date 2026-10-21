import streamlit as st

# Bring in the two backend functions: one loads the CSV, the other scores roles.
from backend.matching import load_role_skills, match_roles

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
    ["Python", "SQL", "Excel", "Machine Learning", "Cloud Computing"]
)

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
        # Rank all roles against the user's selected skills (best match first).
        results = match_roles(skills, role_skills)

        st.subheader("Your Career Matches")

        # Show each role one by one.
        for r in results:
            # Role name with the score shown as a percentage, e.g. 0.667 -> 67%.
            st.markdown(f"**{r['role']}** — {r['score']:.0%} match")

            # A progress bar that fills up to the score (0 to 1).
            st.progress(r["score"])

            # List the skills the user already has for this role, if any.
            if r["matched"]:
                st.write("✅ You have: " + ", ".join(r["matched"]))

            # List the skills the user still needs to learn, if any.
            if r["missing"]:
                st.write("📚 To learn: " + ", ".join(r["missing"]))