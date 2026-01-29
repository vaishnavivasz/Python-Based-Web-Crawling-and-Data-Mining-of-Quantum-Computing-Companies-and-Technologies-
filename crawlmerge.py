import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import re

INPUT_HTML = "dst_nqm.html"
OUTPUT_FILE = "all_quantum_data.json"
WIKI_URL = "https://en.wikipedia.org/wiki/List_of_companies_involved_in_quantum_computing,_communication_or_sensing"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def clean_text(text):
    """Remove citations and strip text."""
    text = re.sub(r"\[\d+\]", "", text)
    return text.strip()

def extract_local_hubs():
    html_path = Path(INPUT_HTML)
    if not html_path.exists():
        print("❌ dst_nqm.html not found")
        return []

    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    table = soup.find("table")
    if not table:
        print("❌ No table found in the HTML")
        return []

    hubs = []
    rows = table.find_all("tr")[1:]  
    for row in rows:
        cols = row.find_all(["td", "th"])
        if len(cols) >= 3:
            hub_name = clean_text(cols[1].get_text())
            technology_domain = clean_text(cols[2].get_text())
            hubs.append({
                "company": hub_name,
                "quantum_products": [technology_domain],
                "source": "dst_nqm_hubs"
            })
    return hubs


def crawl_wikipedia_quantum():
    try:
        response = requests.get(WIKI_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print("❌ Failed to fetch Wikipedia:", e)
        return []

    data = []

    table = soup.find("table", {"class": "wikitable"})
    if not table:
        print("❌ Could not find the list table on Wikipedia.")
        return data

    headers = [clean_text(th.get_text()) for th in table.find_all("th")]
    try:
        company_idx = headers.index("Company")
        tech_idx = headers.index("Technology")
    except ValueError:
        print("❌ Expected columns not found.")
        return data

    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) <= max(company_idx, tech_idx):
            continue
        company = clean_text(cols[company_idx].get_text(" ", strip=True))
        tech = clean_text(cols[tech_idx].get_text(" ", strip=True))
        if company and tech:
            data.append({
                "company": company,
                "quantum_products": [t.strip() for t in re.split(r",|;| and ", tech) if t.strip()],
                "source": "Wikipedia"
            })
    return data


if __name__ == "__main__":
    all_data = []


    all_data.extend(extract_local_hubs())

 
    all_data.extend(crawl_wikipedia_quantum())

    unique_keys = set()
    final_data = []
    for d in all_data:
        key = (d["company"].lower(), d["quantum_products"][0].lower())
        if key not in unique_keys:
            final_data.append(d)
            unique_keys.add(key)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Total records saved: {len(final_data)}")
