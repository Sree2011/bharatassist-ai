import streamlit as st

from agents import (
    OCCUPATIONS,
    STATES,
    citizen_profiler,
    document_agent,
    explain_and_plan,
    planner_agent,
    scheme_finder,
)

st.set_page_config(
    page_title="BharatAssist AI",
    page_icon="🇮🇳",
    layout="wide",
)

st.title("🇮🇳 BharatAssist AI")
st.subheader("Multi-Agent Citizen Welfare Navigator")
st.caption(
    "Not a government website. Always verify details on the official portal "
    "before applying."
)

# ---------------------------------------------------------------- inputs

with st.sidebar:
    st.header("Your profile")

    age = st.number_input("Age", min_value=10, max_value=100, value=25)
    occupation = st.selectbox("Occupation", OCCUPATIONS)
    income = st.number_input(
        "Annual family income (₹)",
        min_value=0,
        max_value=5000000,
        value=100000,
        step=10000,
    )
    state = st.selectbox("State", STATES)
    language = st.selectbox(
        "Explanation language",
        ["English", "Hindi", "Tamil", "Bengali", "Telugu", "Marathi"],
    )

    find = st.button("Find eligible schemes", type="primary", use_container_width=True)

# ---------------------------------------------------------------- results

if find:
    profile = citizen_profiler(age, state, occupation, income)
    result = scheme_finder(profile)
    eligible = result["eligible"]

    if not eligible:
        st.warning("No schemes matched your profile.")
    else:
        st.success(f"Found {len(eligible)} scheme(s) you may qualify for.")

        for scheme in eligible:
            with st.container(border=True):
                head, badge = st.columns([4, 1])
                with head:
                    st.subheader(scheme["name"])
                with badge:
                    st.caption(f"Verified {scheme['last_verified']}")

                st.write(f"**Benefit:** {scheme['benefit']}")

                st.write("**Why you qualify**")
                for reason in scheme["reasons"]:
                    st.write(f"- {reason}")

                with st.expander("Required documents"):
                    for doc in document_agent(scheme):
                        st.write(f"✅ {doc}")

                with st.expander("Application roadmap"):
                    for i, step in enumerate(planner_agent(scheme), 1):
                        st.write(f"{i}. {step}")

                st.link_button("Open official portal", scheme["portal"])

        st.divider()
        if st.button("Generate personalised explanation and plan"):
            with st.spinner("Thinking..."):
                try:
                    text = explain_and_plan(profile, eligible, language)
                    st.markdown(text)
                except Exception as exc:
                    st.error(f"Could not generate explanation: {exc}")

    if result["near_miss"]:
        st.divider()
        st.subheader("Close, but not eligible")
        st.caption("These schemes have income limits you are just above.")
        for scheme in result["near_miss"]:
            with st.container(border=True):
                st.write(f"**{scheme['name']}**")
                for reason in scheme["reasons"]:
                    st.write(f"- {reason}")
                st.link_button("Check official rules", scheme["portal"])