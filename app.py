import streamlit as st

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
    st.write("Profile submitted. Career matching will be connected next.")