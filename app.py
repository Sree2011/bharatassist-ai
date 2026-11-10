import streamlit as st
import pandas as pd

# Load dataset
df = pd.read_csv("./assets/schemes.csv")

st.set_page_config(
    page_title="BharatAssist AI",
    page_icon="🇮🇳",
    layout="wide"
)

st.title("🇮🇳 BharatAssist AI")
st.subheader("Multi-Agent Citizen Welfare Navigator")

# User Inputs
occupation = st.selectbox(
    "Select Occupation",
    sorted(df["occupation"].unique())
)

income = st.number_input(
    "Annual Income (₹)",
    min_value=0,
    value=100000
)

state = st.text_input(
    "State",
    value="All"
)

if st.button("Find Eligible Schemes"):

    results = df[
        (df["occupation"] == occupation)
        & (df["income_limit"] >= income)
    ]

    if len(results) == 0:
        st.warning("No schemes found for the selected profile.")
    else:
        st.success(f"Found {len(results)} eligible schemes")

        for _, scheme in results.iterrows():

            with st.container(border=True):

                st.subheader(scheme["name"])

                st.write(
                    f"**Benefit:** {scheme['benefit']}"
                )

                st.write(
                    f"**Eligible Occupation:** {scheme['occupation']}"
                )

                st.write(
                    f"**State:** {scheme['state']}"
                )

                docs = scheme["documents"].split(";")

                st.write("### Required Documents")

                for doc in docs:
                    st.write(f"✅ {doc}")

                st.link_button(
                    "Apply Here",
                    scheme["portal"]
                )