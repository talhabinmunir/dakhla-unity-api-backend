import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import re
import json

# Path inside the dataset (check the dataset page for exact filename)
file_path = "universities.csv"

df = kagglehub.load_dataset(
    KaggleDatasetAdapter.PANDAS,
    "whisperingkahuna/hec-accredited-universities-of-pakistan-dataset",
    file_path
)


# --- 2. Inspect original columns ---
print("Raw CSV columns:", df.columns.tolist())

# --- 3. Rename to match Unity model fields ---
column_map = {
    "University Name":   "name",
    "City":              "city",
    "Province":          "province",
    "Sector":            "sector",
    "Website":           "websiteUrl",
    "Programs Offered":  "programs_offered",   # temporary
    "Contact Information": "contact_raw",      # temporary
}
df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

# --- 4. Create slug 'id' from name ---
def slugify(text):
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

df["id"] = df["name"].map(slugify)

# --- 5. Combine city + province into 'location' ---
df["location"] = df.get("city", "").fillna("") + ", " + df.get("province", "").fillna("")
df = df.drop(columns=["city", "province"], errors="ignore")

# --- 6. Parse contact_raw into phone, email, address ---
def parse_contact_info(raw):
    text = str(raw or "")
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phones = re.findall(r"\+?\d[\d\-\s()]{7,}\d", text)
    email = emails[0] if emails else ""
    phone = phones[0] if phones else ""
    cleaned = text.replace(email, "").replace(phone, "")
    cleaned = re.sub(r"Address[:\s]*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[;\|]", ",", cleaned).strip(",; ")
    address = cleaned.strip()
    return phone.strip(), email.strip(), address

contact_parsed = df["contact_raw"].apply(parse_contact_info).tolist()
df[["contactPhone", "contactEmail", "address"]] = pd.DataFrame(contact_parsed, index=df.index)
df = df.drop(columns=["contact_raw"], errors="ignore")

# --- 7. Parse programs_offered into structured list ---
def parse_programs(cell, uni_id):
    raw = str(cell or "")
    items = [p.strip() for p in raw.split(";") if p.strip()]
    return [
        {
            "programId": f"{uni_id}-{i}",
            "name":       prog,
            "minRequiredPercentage": None,
            "duration":              None,
            "applicationDeadline":   None,
            "streamTags":            []
        }
        for i, prog in enumerate(items)
    ]

df["programs"] = df.apply(lambda r: parse_programs(r.get("programs_offered"), r["id"]), axis=1)
df = df.drop(columns=["programs_offered"], errors="ignore")

# --- 8. Ensure mandatory columns exist & fill missing ---
for col in ["id","name","location","sector","websiteUrl","contactPhone","contactEmail","address","programs"]:
    if col not in df.columns:
        df[col] = "" if col != "programs" else []
df["sector"] = df["sector"].fillna("")
df["websiteUrl"] = df["websiteUrl"].fillna("")
df["contactPhone"] = df["contactPhone"].fillna("")
df["contactEmail"] = df["contactEmail"].fillna("")
df["address"] = df["address"].fillna("")

# --- 9. Build final JSON structure ---
universities = []
for _, row in df.iterrows():
    universities.append({
        "id":           row["id"],
        "name":         row["name"],
        "location":     row["location"],
        "sector":       row["sector"],
        "websiteUrl":   row["websiteUrl"],
        "contactPhone": row["contactPhone"],
        "contactEmail": row["contactEmail"],
        "address":      row["address"],
        "programs":     row["programs"],
    })

output = {"universities": universities}

# --- 10. Write to JSON file ---
with open("universities.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(universities)} universities to universities.json")

