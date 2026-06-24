#!/usr/bin/env python3
"""
SR Voyages â€” NAP Citation Checker
Checks if SR Voyages is listed on key Senegalese business directories.
Runs via GitHub Actions to monitor citation presence.
"""

import requests
import datetime

SITE = "srvoyages.com"
NAP = {
    "name": "SR Voyages",
    "phone": "+221 77 143 71 25",
    "address": "Avenue LÃ©opold SÃ©dar Senghor, ThiÃ¨s",
}

DIRECTORIES = [
    {"name": "GoAfricaOnline", "url": "https://www.goafricaonline.com/sn/annuaire/agences-de-voyages"},
    {"name": "Senegal-Online", "url": "https://www.senegal-online.com/tourisme_au_senegal/agences-de-voyages-au-senegal/"},
    {"name": "Petit FutÃ©", "url": "https://www.petitfute.com/v37547-thies/c1122-voyage-transports/"},
    {"name": "Annuaire-Senegal", "url": "https://www.annuaire-senegal.com/"},
    {"name": "Afrikta Senegal", "url": "https://afrikta.com/listing-locations/senegal/"},
    {"name": "SenPages", "url": "https://www.senpages.com/"},
    {"name": "Expat.com Senegal", "url": "https://expat.com/fr/entreprises/afrique/senegal/5_tourisme/agences-de-voyage"},
    {"name": "Pages Jaunes Afrique", "url": "https://www.lespagesjaunesafrique.com/societes/senegal/agences-de-voyages/"},
]

def check_directory(directory):
    """Check if SR Voyages is mentioned on the directory page."""
    try:
        resp = requests.get(
            directory["url"],
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; SRVoyages-CitationChecker/1.0)"}
        )
        if resp.status_code == 200:
            found = "sr voyages" in resp.text.lower() or "srvoyages" in resp.text.lower()
            return {"name": directory["name"], "status": "FOUND" if found else "NOT FOUND", "http": 200}
        return {"name": directory["name"], "status": f"HTTP {resp.status_code}", "http": resp.status_code}
    except Exception as e:
        return {"name": directory["name"], "status": f"ERROR: {str(e)[:50]}", "http": 0}

if __name__ == "__main__":
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    print(f"=== SR Voyages Citation Check â€” {now} ===")
    print(f"NAP: {NAP['name']} | {NAP['address']} | {NAP['phone']}")
    print()

    found_count = 0
    for d in DIRECTORIES:
        result = check_directory(d)
        icon = "+" if result["status"] == "FOUND" else "-"
        print(f"  [{icon}] {result['name']}: {result['status']}")
        if result["status"] == "FOUND":
            found_count += 1

    print()
    print(f"=== Citations: {found_count}/{len(DIRECTORIES)} directories ===")
    if found_count < len(DIRECTORIES):
        missing = len(DIRECTORIES) - found_count
        print(f"  Action needed: {missing} directories still need SR Voyages listing")
