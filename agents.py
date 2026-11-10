import json

with open("schemes.json", "r") as f:
    SCHEMES = json.load(f)


def citizen_profiler(age, state, occupation, income):
    return {
        "age": age,
        "state": state,
        "occupation": occupation,
        "income": income
    }


def scheme_finder(profile):
    matches = []

    for scheme in SCHEMES:
        if (
            scheme["occupation"].lower()
            == profile["occupation"].lower()
            and profile["income"]
            <= scheme["income_limit"]
        ):
            matches.append(scheme)

    return matches


def document_agent():
    return [
        "Aadhaar Card",
        "Income Certificate",
        "Bank Passbook"
    ]


def planner_agent():
    return [
        "Collect documents",
        "Verify eligibility",
        "Apply through portal",
        "Track application"
    ]