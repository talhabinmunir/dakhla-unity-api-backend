#!/usr/bin/env python3
"""
Top-10 Pakistani Universities Program Data for DAKHILA App

This script loads the HEC Kaggle dataset (via kagglehub),
filters to a fixed list of 10 well-known universities, and
assigns hardcoded undergraduate program lists for each.

Outputs:
  • universities.json           – array of university metadata + programs
  • programs_by_university.json – map of uni_id → its programs list

The top-10 universities (and their slug IDs) are:
  • NUST                          → national-university-of-sciences-technology
  • LUMS                          → lahore-university-of-management-sciences
  • UET (Lahore)                  → university-of-engineering-technology
  • COMSATS                       → comsats-university
  • FAST (NUCES)                  → fast-nuces
  • University of the Punjab      → university-of-the-punjab
  • Quaid-i-Azam University       → quaid-i-azam-university
  • Aga Khan University           → aga-khan-university
  • IBA Karachi                   → institute-of-business-administration-karachi
  • NED University (Karachi)      → ned-university-of-engineering-technology
"""

import json
import re

import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd

# ─── Configuration ─────────────────────────────────────────────────────────────

# Kagglehub dataset & file path
DATASET_SLUG = "whisperingkahuna/hec-accredited-universities-of-pakistan-dataset"
CSV_FILE_PATH = "universities.csv"  # adjust if needed

# Output files
OUT_UNIS = "universities.json"
OUT_PROGS = "programs_by_university.json"

# Helper: convert full name to slug
def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

# Top-10 university slugs and their hardcoded program lists
HARDCODED_PROGRAMS = {
    "national-university-of-sciences-technology": [
        {"programId": "nust-1", "name": "BSc Electrical Engineering", "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-06-30", "streamTags": ["Engineering"]},
        {"programId": "nust-2", "name": "BS Computer Science",               "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-06-30", "streamTags": ["Engineering", "IT"]},
        {"programId": "nust-3", "name": "BS Civil Engineering",               "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-06-30", "streamTags": ["Engineering"]},
        {"programId": "nust-4", "name": "BS Mechanical Engineering",          "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-06-30", "streamTags": ["Engineering"]},
        {"programId": "nust-5", "name": "BBA",                                 "minRequiredPercentage": 70, "duration": "4 years", "applicationDeadline": "2025-06-30", "streamTags": ["Business"]}
    ],
    "lahore-university-of-management-sciences": [
        {"programId": "lums-1", "name": "BS Computer Science",          "minRequiredPercentage": 65, "duration": "4 years", "applicationDeadline": "2025-04-15", "streamTags": ["IT"]},
        {"programId": "lums-2", "name": "BS Economics",               "minRequiredPercentage": 65, "duration": "4 years", "applicationDeadline": "2025-04-15", "streamTags": ["Arts"]},
        {"programId": "lums-3", "name": "BS Accounting & Finance",      "minRequiredPercentage": 65, "duration": "4 years", "applicationDeadline": "2025-04-15", "streamTags": ["Business"]},
        {"programId": "lums-4", "name": "BS Biology",                  "minRequiredPercentage": 65, "duration": "4 years", "applicationDeadline": "2025-04-15", "streamTags": ["Science"]}
    ],
    "university-of-engineering-technology": [
        {"programId": "uet-1", "name": "BS Civil Engineering",           "minRequiredPercentage": 70, "duration": "4 years", "applicationDeadline": "2025-06-01", "streamTags": ["Engineering"]},
        {"programId": "uet-2", "name": "BS Electrical Engineering",      "minRequiredPercentage": 70, "duration": "4 years", "applicationDeadline": "2025-06-01", "streamTags": ["Engineering"]},
        {"programId": "uet-3", "name": "BS Mechanical Engineering",      "minRequiredPercentage": 70, "duration": "4 years", "applicationDeadline": "2025-06-01", "streamTags": ["Engineering"]},
        {"programId": "uet-4", "name": "BS Computer Engineering",        "minRequiredPercentage": 80, "duration": "4 years", "applicationDeadline": "2025-06-01", "streamTags": ["Engineering", "IT"]}
    ],
    "comsats-university": [
        {"programId": "comsats-1", "name": "BS Electrical Engineering",   "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-07-25", "streamTags": ["Engineering"]},
        {"programId": "comsats-2", "name": "BS Computer Science",         "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-07-25", "streamTags": ["Engineering", "IT"]},
        {"programId": "comsats-3", "name": "BS Civil Engineering",        "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-07-25", "streamTags": ["Engineering"]},
        {"programId": "comsats-4", "name": "BS Software Engineering",     "minRequiredPercentage": 70, "duration": "4 years", "applicationDeadline": "2025-07-25", "streamTags": ["IT"]}
    ],
    "fast-nuces": [
        {"programId": "fast-1", "name": "BS Computer Science",            "minRequiredPercentage": 60, "duration": "4 years", "applicationDeadline": "2025-07-04", "streamTags": ["Engineering", "IT"]},
        {"programId": "fast-2", "name": "BS Electrical Engineering",      "minRequiredPercentage": 60, "duration": "4 years", "applicationDeadline": "2025-07-04", "streamTags": ["Engineering"]},
        {"programId": "fast-3", "name": "BS Civil Engineering",           "minRequiredPercentage": 60, "duration": "4 years", "applicationDeadline": "2025-07-04", "streamTags": ["Engineering"]},
        {"programId": "fast-4", "name": "BS Software Engineering",        "minRequiredPercentage": 60, "duration": "4 years", "applicationDeadline": "2025-07-04", "streamTags": ["IT"]}
    ],
    "university-of-the-punjab": [
        {"programId": "pu-1", "name": "BS Computer Science",              "minRequiredPercentage": 70, "duration": "4 years", "applicationDeadline": "2025-05-26", "streamTags": ["Engineering", "IT"]},
        {"programId": "pu-2", "name": "BS Electrical Engineering",        "minRequiredPercentage": 70, "duration": "4 years", "applicationDeadline": "2025-05-26", "streamTags": ["Engineering"]},
        {"programId": "pu-3", "name": "BS Civil Engineering",             "minRequiredPercentage": 70, "duration": "4 years", "applicationDeadline": "2025-05-26", "streamTags": ["Engineering"]},
        {"programId": "pu-4", "name": "BS Business Administration",       "minRequiredPercentage": 65, "duration": "4 years", "applicationDeadline": "2025-05-26", "streamTags": ["Business"]}
    ],
    "quaid-i-azam-university": [
        {"programId": "qau-1", "name": "BS Computer Science",             "minRequiredPercentage": 65, "duration": "4 years", "applicationDeadline": "2025-06-01", "streamTags": ["Engineering", "IT"]},
        {"programId": "qau-2", "name": "BS Economics",                    "minRequiredPercentage": 65, "duration": "4 years", "applicationDeadline": "2025-06-01", "streamTags": ["Arts"]},
        {"programId": "qau-3", "name": "BS Environmental Sciences",       "minRequiredPercentage": 65, "duration": "4 years", "applicationDeadline": "2025-06-01", "streamTags": ["Science"]},
        {"programId": "qau-4", "name": "BA-LL.B (Honours)",               "minRequiredPercentage": 70, "duration": "5 years", "applicationDeadline": "2025-06-01", "streamTags": ["Law"]}
    ],
    "aga-khan-university": [
        {"programId": "aku-1", "name": "MBBS",                             "minRequiredPercentage": 80, "duration": "5 years", "applicationDeadline": "2025-04-30", "streamTags": ["Medical"]},
        {"programId": "aku-2", "name": "BSc Nursing",                      "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-04-30", "streamTags": ["Medical"]},
        {"programId": "aku-3", "name": "BS Computer Science",              "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-04-30", "streamTags": ["IT"]}
    ],
    "institute-of-business-administration-karachi": [
        {"programId": "iba-1", "name": "BBA",                              "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-06-15", "streamTags": ["Business"]},
        {"programId": "iba-2", "name": "BS Accounting & Finance",          "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-06-15", "streamTags": ["Business"]},
        {"programId": "iba-3", "name": "BS Economics",                     "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-06-15", "streamTags": ["Arts"]},
        {"programId": "iba-4", "name": "BS Mathematics",                   "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-06-15", "streamTags": ["Science"]}
    ],
    "ned-university-of-engineering-technology": [
        {"programId": "ned-1", "name": "BS Computer Science",             "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-06-01", "streamTags": ["Engineering", "IT"]},
        {"programId": "ned-2", "name": "BS Mechanical Engineering",       "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-06-01", "streamTags": ["Engineering"]},
        {"programId": "ned-3", "name": "BS Civil Engineering",            "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-06-01", "streamTags": ["Engineering"]},
        {"programId": "ned-4", "name": "BS Electrical Engineering",       "minRequiredPercentage": 75, "duration": "4 years", "applicationDeadline": "2025-06-01", "streamTags": ["Engineering"]}
    ],
}

def main():
    # 1) Load Kaggle dataset into DataFrame
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        DATASET_SLUG,
        CSV_FILE_PATH
    )
    print("Loaded Kaggle DataFrame columns:", df.columns.tolist())

    universities_output = []
    programs_map = {}

    # 2) Iterate and pick only top-10 universities
    for _, row in df.iterrows():
        name = str(row.get("University Name", "")).strip()
        website = str(row.get("Website", "")).strip()
        city = str(row.get("City", "")).strip()
        prov = str(row.get("Province", "")).strip()
        sector = str(row.get("Sector", "")).strip()

        if not name or not website:
            continue

        slug = slugify(name)
        if slug not in HARDCODED_PROGRAMS:
            continue  # skip non-top-10

        uni_entry = {
            "id": slug,
            "name": name,
            "location": f"{city}, {prov}".strip(", "),
            "sector": sector,
            "websiteUrl": website,
            "contactPhone": "",
            "contactEmail": "",
            "address": "",
            "logoUrl": "",
            "programs": HARDCODED_PROGRAMS[slug]
        }

        universities_output.append(uni_entry)
        programs_map[slug] = HARDCODED_PROGRAMS[slug]

    # 3) Write out JSON files
    with open(OUT_UNIS, "w", encoding="utf-8") as f:
        json.dump(universities_output, f, ensure_ascii=False, indent=2)
    with open(OUT_PROGS, "w", encoding="utf-8") as f:
        json.dump(programs_map, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(universities_output)} universities to {OUT_UNIS}")
    print(f"Wrote programs map to {OUT_PROGS}")

if __name__ == "__main__":
    main()
