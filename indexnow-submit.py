#!/usr/bin/env python3
"""
Automated URL indexation for srvoyages.com
Fetches sitemap, extracts URLs, submits to IndexNow (Bing/Yandex)
and pings Google sitemap endpoint.

Used by GitHub Actions workflow on a daily schedule.
"""

import xml.etree.ElementTree as ET
import requests
import json
import sys

SITE = "srvoyages.com"
INDEXNOW_KEY = "srvoyages2026indexnow"
SITEMAP_INDEX = f"https://{SITE}/sitemap_index.xml"

def fetch_sitemap_urls():
    """Fetch all URLs from sitemap index and child sitemaps."""
    urls = []
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    # Fetch sitemap index
    resp = requests.get(SITEMAP_INDEX, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    sitemaps = [loc.text for loc in root.findall(".//sm:loc", ns)]
    print(f"Found {len(sitemaps)} sitemaps in index")

    for sitemap_url in sitemaps:
        # Skip author sitemap (no SEO value)
        if "author" in sitemap_url:
            continue
        try:
            resp = requests.get(sitemap_url, timeout=30)
            resp.raise_for_status()
            child = ET.fromstring(resp.content)
            child_urls = [loc.text for loc in child.findall(".//sm:loc", ns)]
            urls.extend(child_urls)
            print(f"  {sitemap_url}: {len(child_urls)} URLs")
        except Exception as e:
            print(f"  ERROR fetching {sitemap_url}: {e}")

    return urls

def submit_indexnow(urls):
    """Submit URLs to IndexNow API (Bing, Yandex, Seznam, Naver)."""
    if not urls:
        print("No URLs to submit")
        return False

    # IndexNow accepts max 10000 URLs per request
    batch_size = 100
    total_submitted = 0

    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        payload = {
            "host": SITE,
            "key": INDEXNOW_KEY,
            "keyLocation": f"https://{SITE}/{INDEXNOW_KEY}.txt",
            "urlList": batch
        }

        try:
            resp = requests.post(
                "https://api.indexnow.org/indexnow",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            if resp.status_code in (200, 202):
                total_submitted += len(batch)
                print(f"  IndexNow batch {i//batch_size + 1}: {len(batch)} URLs submitted (HTTP {resp.status_code})")
            else:
                print(f"  IndexNow batch {i//batch_size + 1}: HTTP {resp.status_code} - {resp.text[:200]}")
        except Exception as e:
            print(f"  IndexNow batch {i//batch_size + 1}: ERROR - {e}")

    print(f"Total submitted to IndexNow: {total_submitted}/{len(urls)}")
    return total_submitted > 0

def ping_google_sitemap():
    """Ping Google with the sitemap URL."""
    ping_url = f"https://www.google.com/ping?sitemap=https://{SITE}/sitemap_index.xml"
    try:
        resp = requests.get(ping_url, timeout=30)
        print(f"Google sitemap ping: HTTP {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Google sitemap ping: ERROR - {e}")
        return False

def ping_bing_sitemap():
    """Ping Bing with the sitemap URL."""
    ping_url = f"https://www.bing.com/ping?sitemap=https://{SITE}/sitemap_index.xml"
    try:
        resp = requests.get(ping_url, timeout=30)
        print(f"Bing sitemap ping: HTTP {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Bing sitemap ping: ERROR - {e}")
        return False

if __name__ == "__main__":
    print(f"=== IndexNow Submission for {SITE} ===")
    print()

    # 1. Fetch all URLs from sitemaps
    print("1. Fetching sitemap URLs...")
    urls = fetch_sitemap_urls()
    print(f"   Total URLs found: {len(urls)}")
    print()

    # 2. Submit to IndexNow
    print("2. Submitting to IndexNow (Bing, Yandex, Seznam, Naver)...")
    submit_indexnow(urls)
    print()

    # 3. Ping Google
    print("3. Pinging Google sitemap...")
    ping_google_sitemap()
    print()

    # 4. Ping Bing
    print("4. Pinging Bing sitemap...")
    ping_bing_sitemap()
    print()

    print(f"=== Done. {len(urls)} URLs processed. ===")
