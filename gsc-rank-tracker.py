"""GSC Rank Tracker — Positions réelles Google via Search Console API.

Complète rank-tracker.py (qui ne fait que du health-check) en récupérant
les vraies positions moyennes, clics, impressions et CTR pour SR Voyages,
avec distinction local (Thiès/Dakar) vs national.
"""

import csv
import datetime
import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
SITE_URL = "https://srvoyages.com/"
LOCAL_KEYWORDS = ["thies", "thiès", "dakar"]
OUTPUT_DIR = "reports"
DAYS_LOOKBACK = 3

def get_service():
    key_json = os.environ["GSC_SERVICE_ACCOUNT_JSON"]
    info = json.loads(key_json)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("searchconsole", "v1", credentials=creds)

def classify_scope(query):
    q = query.lower()
    return "local" if any(kw in q for kw in LOCAL_KEYWORDS) else "national"

def fetch_rankings(service, start_date, end_date):
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["query", "page", "country"],
        "rowLimit": 5000,
    }
    response = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
    return response.get("rows", [])

def write_csv(rows, date_str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, f"gsc-rankings-{date_str}.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["query", "page", "country", "scope", "position", "clicks", "impressions", "ctr"])
        for row in rows:
            query, page, country = row["keys"]
            writer.writerow([
                query, page, country, classify_scope(query),
                round(row["position"], 1), row["clicks"], row["impressions"],
                round(row["ctr"] * 100, 2),
            ])
    return filepath

def generate_report():
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")
    print(f"=== GSC Rank Report for {SITE_URL} — {now} ===")

    service = get_service()
    end = datetime.datetime.now(datetime.UTC).date() - datetime.timedelta(days=2)
    start = end - datetime.timedelta(days=DAYS_LOOKBACK)
    date_str = end.isoformat()

    rows = fetch_rankings(service, start.isoformat(), end.isoformat())
    if not rows:
        print("  Aucune donnée GSC disponible pour cette période.")
        return

    filepath = write_csv(rows, date_str)
    print(f"  {len(rows)} lignes -> {filepath}")

    tracked_lower = {
        "agence de voyage thiès", "agence de voyage sénégal", "agence de voyage dakar",
        "billet avion pas cher dakar", "billet avion dakar paris", "visa schengen sénégal",
        "visa canada sénégal", "visa usa sénégal", "hajj 2027 sénégal", "omra sénégal",
        "sr voyages thiès",
    }
    print("\n  Positions sur mots-clés suivis (correspondance approximative):")
    for row in rows:
        query = row["keys"][0].lower()
        if any(k in query for k in tracked_lower):
            print(f"    [{classify_scope(query)}] {row['keys'][0]}: position {round(row['position'], 1)}")

if __name__ == "__main__":
    generate_report()
