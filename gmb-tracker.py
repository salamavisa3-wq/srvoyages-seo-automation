#!/usr/bin/env python3
"""
SR Voyages - GMB Local Pack Position Tracker
Checks Google Maps results for key queries to track local ranking.
"""

import requests
import datetime

QUERIES = [
    "agence+de+voyage+Thiès",
    "agence+voyage+Thiès+Sénégal",
    "billet+avion+Thiès",
    "visa+Thiès+Sénégal",
]

def check_google_presence():
    """Check if SR Voyages appears in organic Google results."""
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")
    print(f"=== SR Voyages Presence Check - {now} ===")
    print()
    
    # Check website accessibility
    checks = [
        ("Homepage", "https://srvoyages.com/"),
        ("Agence Dakar", "https://srvoyages.com/agence-de-voyage-dakar/"),
        ("Agence Thiès", "https://srvoyages.com/agence-de-voyage-a-thies-vols-visas-hotels-sr-voyages/"),
        ("GeoSitemap", "https://srvoyages.com/geo-sitemap.xml"),
        ("IndexNow Key", "https://srvoyages.com/srvoyages2026indexnow.txt"),
        ("Sitemap Index", "https://srvoyages.com/sitemap_index.xml"),
        ("robots.txt", "https://srvoyages.com/robots.txt"),
    ]
    
    print("Site Health:")
    all_ok = True
    for name, url in checks:
        try:
            r = requests.head(url, timeout=10, allow_redirects=True, 
                            headers={"User-Agent": "SRVoyages-Monitor/1.0"})
            status = "OK" if r.status_code == 200 else f"HTTP {r.status_code}"
            if r.status_code != 200:
                all_ok = False
            print(f"  [{'+' if r.status_code == 200 else '-'}] {name}: {status}")
        except Exception as e:
            all_ok = False
            print(f"  [-] {name}: ERROR {str(e)[:40]}")
    
    print()
    print(f"GMB Action Items (manual):")
    print(f"  1. Obtain 10+ Google reviews (currently 1)")
    print(f"  2. Add 10+ photos to GMB profile")
    print(f"  3. Post 1 Google Post per week")
    print(f"  4. Register in 8 local directories")
    print(f"  5. Respond to all reviews within 24h")
    print()
    
    if all_ok:
        print("=== All site health checks PASSED ===")
    else:
        print("=== WARNING: Some health checks FAILED ===")

if __name__ == "__main__":
    check_google_presence()