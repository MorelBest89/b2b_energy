"""Test undetected-playwright against Google search."""
import csv, re, random, time
from playwright.sync_api import sync_playwright
from undetected_playwright import stealth_sync

CSV_PATH = r"C:\Users\marco\Projects\consulenza_energy\data\contatti_b2b.csv"
with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    all_rows = list(csv.DictReader(f))

sample = random.sample(all_rows, 2)
print("undetected-playwright test — 5 Google searches\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        locale="it-IT",
        viewport={"width": 1024, "height": 700},
    )
    context = stealth_sync(context)  # Apply undetected patch
    page = context.new_page()

    for i, r in enumerate(sample):
        name = r["nome"].strip()
        city = r["citta"].strip()
        print(f"[{i+1}] {name[:50]} | {city}", flush=True)

        try:
            # Direct search URL (no typing)
            search_url = f"https://www.google.com/search?q={name.replace(' ', '+')}+{city.replace(' ', '+')}&hl=it"
            page.goto(search_url, wait_until="networkidle", timeout=20000)
            page.wait_for_timeout(random.randint(2000, 4000))

            body = page.inner_text("body")
            
            if any(k in body.lower() for k in ["captcha", "insolit", "robot"]):
                print("  CAPTCHA!", flush=True)
                continue

            # DEBUG: print all links found
            all_hrefs = []
            for link in page.query_selector_all("a[href]"):
                h = link.get_attribute("href") or ""
                if h and len(h) > 15:
                    all_hrefs.append(h)
            print(f"  Links found: {len(all_hrefs)}", flush=True)
            for h in all_hrefs[:5]:
                print(f"    {h[:120]}", flush=True)

            # Get first real result URL
            site = ""
            for link in page.query_selector_all("div#search a[href^='http'], div#search a[href^='/url']"):
                href = link.get_attribute("href") or ""
                if "/url?q=" in href:
                    m = re.search(r'/url\?q=([^&]+)', href)
                    if m:
                        href = m.group(1)
                if len(href) < 25 or "youtube.com" in href or "/accounts/" in href or "google.com" in href:
                    continue
                site = href
                break
            
            if not site:
                for link in page.query_selector_all("a[href^='/url?q=']"):
                    href = link.get_attribute("href") or ""
                    m = re.search(r'/url\?q=([^&]+)', href)
                    if m:
                        real_url = m.group(1)
                        if len(real_url) > 25 and "google" not in real_url:
                            site = real_url
                            break
            
            # Fallback: any http link not google
            if not site:
                for h in all_hrefs:
                    if "google" in h or "youtube" in h or "/accounts/" in h or len(h) < 30:
                        continue
                    site = h
                    break

            # Phone from snippets
            phone = ""
            for pat in [r'(\+39[\s\d]{8,15})', r'(\d{2,4}\s\d{3}[\s\-]\d{4})', r'(\d{3}\s\d{3}\s\d{3,4})']:
                m = re.search(pat, body)
                if m:
                    d = re.sub(r'[^\d]', '', m.group(1))
                    if 8 <= len(d) <= 13:
                        phone = m.group(1).strip()
                        break

            print(f"  SITO: {site[:100] if site else 'NOT FOUND'}", flush=True)
            if phone:
                print(f"  TEL: {phone}", flush=True)

        except Exception as e:
            print(f"  ERR: {e}", flush=True)

        page.wait_for_timeout(random.randint(4000, 7000))

    context.close()
    browser.close()

print("\nDone.")
