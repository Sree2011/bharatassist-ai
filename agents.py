"""BharatAssist AI - agent layer.

Deterministic filtering lives in Python. The LLM is used only for
explanation and roadmap generation, where it adds real value.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SCHEMES_PATH = Path(__file__).parent / "schemes.json"

with open(SCHEMES_PATH, encoding="utf-8") as f:
    SCHEMES = json.load(f)

OCCUPATIONS = sorted({occ for s in SCHEMES for occ in s["occupations"]})
STATES = ["All"] + [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry",
]


# ---------------------------------------------------------------- profiling

def citizen_profiler(age: int, state: str, occupation: str, income: int) -> dict:
    """Normalise raw form input into a profile dict."""
    return {
        "age": int(age),
        "state": state.strip(),
        "occupation": occupation.strip(),
        "income": int(income),
    }


# ---------------------------------------------------------------- matching

def _check(scheme: dict, profile: dict) -> tuple[bool, list[str]]:
    """Return (eligible, reasons). Reasons explain the verdict either way."""
    reasons = []

    if profile["occupation"] not in scheme["occupations"]:
        return False, [
            f"Open to {', '.join(scheme['occupations'])}, "
            f"not {profile['occupation']}."
        ]

    if scheme["state"] != "All" and scheme["state"] != profile["state"]:
        return False, [f"Limited to {scheme['state']}."]

    limit = scheme.get("income_limit")
    if limit is not None and profile["income"] > limit:
        gap = profile["income"] - limit
        return False, [
            f"Income limit is ₹{limit:,}. You are ₹{gap:,} above it."
        ]

    if limit is not None:
        reasons.append(
            f"Income ₹{profile['income']:,} is within the ₹{limit:,} limit."
        )
    else:
        reasons.append("No income ceiling for this scheme.")

    if scheme["state"] == "All":
        reasons.append("Available in all states.")

    return True, reasons


def scheme_finder(profile: dict) -> dict:
    """Split schemes into eligible and near-miss buckets."""
    eligible, near_miss = [], []

    for scheme in SCHEMES:
        ok, reasons = _check(scheme, profile)
        record = {**scheme, "reasons": reasons}
        if ok:
            eligible.append(record)
        elif any("above it" in r for r in reasons):
            # Only surface income near-misses; occupation mismatches are noise.
            near_miss.append(record)

    near_miss.sort(
        key=lambda s: s["income_limit"] - profile["income"]
        if s.get("income_limit") else 0
    )
    return {"eligible": eligible, "near_miss": near_miss[:3]}


# ---------------------------------------------------------------- LLM layer

def _client():
    from google import genai
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
    return genai.Client(api_key=key)


def explain_and_plan(profile: dict, schemes: list[dict], language: str = "English") -> str:
    """Template-based explanation. No API key required."""
    if not schemes:
        return "No schemes matched your profile. Try adjusting your occupation or income."

    lines = [
        f"Based on your profile — age {profile['age']}, "
        f"{profile['occupation']}, annual income ₹{profile['income']:,}, "
        f"{profile['state']} — here is what you may qualify for:\n"
    ]

    for s in schemes:
        lines.append(f"### {s['name']}")
        lines.append(f"**Benefit:** {s['benefit']}")
        lines.append(f"**Why you qualify:** {' '.join(s['reasons'])}")
        lines.append(f"**Documents:** {', '.join(s['documents'])}")
        lines.append(f"**Apply at:** {s['portal']}")
        lines.append("")

    lines.append(
        "_This is a prototype. Verify all details on the official portal "
        "before applying._"
    )
    return "\n".join(lines)


def document_agent(scheme: dict) -> list[str]:
    """Union of documents for a scheme, deduplicated, order preserved."""
    seen, out = set(), []
    for doc in scheme.get("documents", []):
        if doc not in seen:
            seen.add(doc)
            out.append(doc)
    return out


def planner_agent(scheme: dict) -> list[str]:
    """Generic application roadmap derived from the scheme record."""
    steps = [
        f"Confirm you meet the criteria: {scheme['eligibility_notes']}",
        "Gather the required documents",
        f"Apply on the official portal: {scheme['portal']}",
        "Note your application or reference number",
        "Track status and respond to any queries",
    ]
    if scheme.get("last_verified"):
        steps.append(
            f"Rules last verified {scheme['last_verified']} - re-check the portal before applying"
        )
    return steps