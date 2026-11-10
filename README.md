# 🇮🇳 BharatAssist AI

Multi-agent citizen welfare navigator for Indian government schemes.

## Problem

Millions of Indian citizens are unaware of welfare schemes they qualify for,
and struggle to understand eligibility rules and application steps.

## What it does

- Profiles a citizen from four inputs: age, occupation, income, state
- Matches them against a curated scheme database using explicit rules
- Explains *why* they qualify, not just that they do
- Surfaces near-miss schemes where income is the only blocker
- Generates a personalised application roadmap in six Indian languages

## Architecture

Filtering is deterministic Python, not an LLM call — eligibility rules
should be auditable. The LLM is used only for explanation and roadmap
generation, grounded strictly in retrieved scheme records.

```mermaid
flowchart LR
    A[Citizen profile] --> B[Rule-based matcher]
    B --> C{Eligible?}
    C -->|Yes| D[Scheme cards + reasons]
    C -->|Near miss| E[Gap explanation]
    D --> F[LLM: explain + roadmap]
    F --> G[Grounded in scheme records]