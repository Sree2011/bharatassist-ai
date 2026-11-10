import streamlit as st
from agents import *

st.title("🇮🇳 BharatAssist AI")

age = st.number_input("Age", 18, 100)
state = st.text_input("State")
occupation = st.selectbox(
    "Occupation",
    ["Student", "Farmer", "Unemployed"]
)

income = st.number_input("Annual Income")

if st.button("Find Schemes"):

    profile = citizen_profiler(
        age,
        state,
        occupation,
        income
    )

    schemes = scheme_finder(profile)

    st.subheader("Eligible Schemes")

    for s in schemes:
        st.success(
            f"{s['name']} - {s['benefit']}"
        )

    st.subheader("Required Documents")

    for doc in document_agent():
        st.write("✅", doc)

    st.subheader("Action Plan")

    for step in planner_agent():
        st.write("➡️", step)