"""Test: extract website from PagineGialle detail pages for 5 contacts."""
import csv, re, time, random
from playwright.sync_api import sync_playwright

CSV_PATH = r"C:\Users\marco\Projects\consulenza_energy\data\contatti_b2b.csv"

with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    all_rows = list(csv.DictReader(f))

# Pick 5 contacts WITHOUT website
no_site = [r for r in all_rows if not r.get("sito", "").strip() and r["fonte"] == "PagineGialle"]
sample = random.sample(no_site, min(5, len(no_site)))

print("PagineGialle detail page — website extraction test\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="it-IT", viewport={"width": 1024, "height": 700},
    )
    page = ctx.new_page()

    for i, r in enumerate(sample):
        name = r["nome"].strip()
        city = r["citta"].strip()
        print(f"[{i+1}] {name[:60]} | {city}")

        try:
            # Search by category + city (much more reliable than name search)
            cat = r["categoria"].strip()
            # Map category to Italian PagineGialle query
            query_map = {
                "Ristoranti/Pizzerie": "ristoranti",
                "Palestre": "palestre",
                "Officine/Artigiani": "officine meccaniche",
                "Lavanderie": "lavanderie industriali",
                "Hotel/B&B": "alberghi",
            }
            q = query_map.get(cat, "ristoranti")
            search_url = f"https://www.paginegialle.it/ricerca/{q}/{city.replace(' ', '%20')}"
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2500)

            # Dismiss cookie
            for sel in ["button:has-text('Accetta')", "#onetrust-accept-btn-handler"]:
                try:
                    page.click(sel, timeout=1000)
                except:
                    pass

            # Scroll to load results
            for _ in range(4):
                page.evaluate("window.scrollBy(0, 1000)")
                page.wait_for_timeout(300)

            # 2. Find the matching business card
            clicked = False
            cards = page.query_selector_all("div.search-itm, div.card-listing")
            for card in cards:
                card_text = card.inner_text().strip()
                # Check if this card matches our business name
                n = name.lower()[:15]
                if n in card_text.lower():
                    # Try to click the card
                    try:
                        card.click()
                        page.wait_for_timeout(2000)
                        clicked = True
                        break
                    except:
                        pass

            if not clicked:
                print("  -> Could not find/click detail link", flush=True)
                continue

            # 3. Extract website from detail page
            body = page.inner_text("body")

            website = ""
            # Look for any external link that's not PagineGialle/Facebook/Google
            for a in page.query_selector_all("a[href^='http']"):
                href = a.get_attribute("href") or ""
                href = href.rstrip("/")
                if len(href) < 25:
                    continue
                if any(k in href.lower() for k in [
                    "paginegialle", "facebook.com/login", "google.com/maps",
                    "1240.it", "prontopro", "instagram.com/accounts",
                ]):
                    continue
                # Prefer links that are NOT social media
                if "facebook.com" not in href and "instagram.com" not in href and "tripadvisor" not in href:
                    website = href
                    break

            # Fallback: accept social/review sites
            if not website:
                for a in page.query_selector_all("a[href^='http']"):
                    href = a.get_attribute("href") or ""
                    if len(href) < 25 or "paginegialle" in href or "google" in href:
                        continue
                    website = href
                    break

            print(f"  SITO: {website[:120] if website else 'NOT FOUND'}", flush=True)

        except Exception as e:
            print(f"  ERR: {e}", flush=True)

        page.wait_for_timeout(random.randint(2000, 4000))

    browser.close()

print("\nDone.")
