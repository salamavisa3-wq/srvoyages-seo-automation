#!/usr/bin/env python3
"""
SR Voyages â€” Google Rank Tracker
Checks search positions for target keywords daily via GitHub Actions.
Uses SerpAPI-compatible free endpoints or logs for manual checking.
"""

import requests
import json
import datetime
import os
import sys

SITE = "srvoyages.com"
KEYWORDS = [
    "agence de voyage ThiÃ¨s",
    "agence de voyage SÃ©nÃ©gal",
    "agence de voyage Dakar",
    "billet avion pas cher Dakar",
    "billet avion Dakar Paris",
    "visa Schengen SÃ©nÃ©gal",
    "visa Canada SÃ©nÃ©gal",
    "visa USA SÃ©nÃ©gal",
    "Hajj 2027 SÃ©nÃ©gal",
    "Omra SÃ©nÃ©gal",
    "agence voyage ThiÃ¨s billets",
    "meilleure agence voyage Dakar",
    "SR Voyages ThiÃ¨s",
    "excursion Saly SÃ©nÃ©gal",
    "vol Dakar New York",
    "vol Dakar Istanbul",
    "billet avion Dakar DubaÃ¯",
    "visa Angleterre SÃ©nÃ©gal",
    "agence IATA SÃ©nÃ©gal",
    "voyage groupe SÃ©nÃ©gal",
]

def check_indexnow_submission():
    """Submit all sitemap URLs to IndexNow as part of daily routine."""
    import xml.etree.ElementTree as ET

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []

    try:
        resp = requests.get(f"https://{SITE}/sitemap_index.xml", timeout=30)
        root = ET.fromstring(resp.content)
        for sitemap_loc in root.findall(".//sm:loc", ns):
            sitemap_url = sitemap_loc.text
            if "author" in sitemap_url:
                continue
            try:
                r = requests.get(sitemap_url, timeout=30)
                child = ET.fromstring(r.content)
                urls.extend([loc.text for loc in child.findall(".//sm:loc", ns)])
            except Exception:
                pass
    except Exception as e:
        print(f"  Sitemap fetch error: {e}")
        return 0

    if not urls:
        return 0

    payload = {
        "host": SITE,
        "key": "srvoyages2026indexnow",
        "keyLocation": f"https://{SITE}/srvoyages2026indexnow.txt",
        "urlList": urls[:100]
    }
    try:
        r = requests.post("https://api.indexnow.org/indexnow", json=payload, timeout=30)
        print(f"  IndexNow batch 1: {min(len(urls), 100)} URLs (HTTP {r.status_code})")
    except Exception as e:
        print(f"  IndexNow error: {e}")

    if len(urls) > 100:
        payload["urlList"] = urls[100:]
        try:
            r = requests.post("https://api.indexnow.org/indexnow", json=payload, timeout=30)
            print(f"  IndexNow batch 2: {len(urls) - 100} URLs (HTTP {r.status_code})")
        except Exception as e:
            print(f"  IndexNow error: {e}")

    return len(urls)

def generate_report():
    """Generate a daily SEO status report."""
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    report = {
        "date": now,
        "site": SITE,
        "keywords_tracked": len(KEYWORDS),
        "keywords": KEYWORDS,
        "actions": []
    }

    # 1. IndexNow submission
    print("1. IndexNow daily submission...")
    count = check_indexnow_submission()
    report["actions"].append(f"IndexNow: {count} URLs submitted")

    # 2. Sitemap ping
    print("2. Sitemap ping to Bing...")
    try:
        r = requests.get(f"https://www.bing.com/ping?sitemap=https://{SITE}/sitemap_index.xml", timeout=15)
        report["actions"].append(f"Bing sitemap ping: HTTP {r.status_code}")
        print(f"  Bing ping: HTTP {r.status_code}")
    except Exception as e:
        report["actions"].append(f"Bing ping error: {e}")

    # 3. Check homepage status
    print("3. Homepage health check...")
    try:
        r = requests.get(f"https://{SITE}/", timeout=15, headers={"User-Agent": "SRVoyages-SEO-Monitor/1.0"})
        report["actions"].append(f"Homepage: HTTP {r.status_code}, {len(r.content)} bytes")
        print(f"  Homepage: HTTP {r.status_code}")
    except Exception as e:
        report["actions"].append(f"Homepage error: {e}")
        print(f"  Homepage error: {e}")

    # 4. Check key pages
    print("4. Key pages health check...")
    key_pages = [
        "/agence-de-voyage-dakar/",
        "/agence-de-voyage-a-thies-vols-visas-hotels-sr-voyages/",
        "/billets-davion-pas-cher-au-senegal-sr-voyages-thies-dakar/",
        "/visa-canada-usa-europe-depuis-le-senegal-sr-voyages/",
        "/hajj-omra-depuis-le-senegal-packages-complets-sr-voyages/",
        "/blog/",
    ]
    for page in key_pages:
        try:
            r = requests.head(f"https://{SITE}{page}", timeout=10, allow_redirects=True)
            status = "OK" if r.status_code == 200 else f"HTTP {r.status_code}"
            print(f"  {page}: {status}")
        except Exception:
            print(f"  {page}: ERROR")

    print(f"\n=== Daily SEO Report for {SITE} â€” {now} ===")
    for action in report["actions"]:
        print(f"  {action}")
    print(f"  Keywords tracked: {len(KEYWORDS)}")
    print(f"  Manual check: search each keyword on google.com/search?gl=sn&q=<keyword>")

    return report

if __name__ == "__main__":
    generate_report()
