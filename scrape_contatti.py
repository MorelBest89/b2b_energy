"""
Multi-source B2B contact scraper for M&M Energy.
Sources:
  1. PagineGialle (headed Playwright) — primary, with pagination + 20+ cities
  2. Google Maps (headed Playwright) — rich data per business
Output: contatti_b2b.csv
"""
import csv, time, re, os, sys
from collections import Counter
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

BASE = r"C:\Users\marco\Projects\consulenza_energy"
OUTPUT = os.path.join(BASE, "contatti_b2b.csv")

# ── CITIES ─────────────────────────────────────────────────────
# Varese province + Como + Lago Maggiore
CITIES = [
    "Varese", "Gallarate", "Busto Arsizio", "Saronno", "Tradate",
    "Malnate", "Luino", "Gavirate", "Somma Lombardo", "Cassano Magnago",
    "Como", "Cantu", "Erba", "Mariano Comense", "Olgiate Comasco",
    "Lomazzo", "Fino Mornasco", "Verbania", "Stresa", "Arona",
]

CATEGORIES = [
    ("Ristoranti/Pizzerie", "ristoranti"),
    ("Palestre", "palestre"),
    ("Officine/Artigiani", "officine meccaniche"),
    ("Lavanderie", "lavanderie industriali"),
    ("Hotel/B&B", "hotel"),
]

# ── HELPERS ────────────────────────────────────────────────────
ADDR_RE = re.compile(
    r"(Via|Piazza|Corso|Viale|Largo|Localit[aà]|Strada|Contrada)\s+.+,\s*\d+\s*[-–]\s*\d{4,5}\s*\S+"
)
SKIP_WORDS = {
    "vedi", "prenota", "mostra", "attiva", "categoria", "ordina per",
    "servizi in", "tipi di", "quartiere", "filtra", "rilevanza", "nuovo",
    "distanza", "popolarit", "risultati fuori", "paginegialle", "accedi",
    "registra", "cerca per", "mostra tutto",
}


def clean_name(raw):
    raw = re.sub(r'\s*\(\d+\)\s*$', '', raw)
    raw = re.sub(r'\s*\d+\.?\d*km$', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'\s*Suggerito\s*$', '', raw)
    raw = re.sub(r'\s*\|\s*\S+$', '', raw)
    return raw.strip()


def extract_cards_pg(page):
    """Extract from PagineGialle search results page."""
    results = []
    cards = page.query_selector_all("div.search-itm.card-listing, div.card-azienda")
    for card in cards:
        try:
            full_text = card.inner_text()
            name_el = card.query_selector(".info-card__title, h2, h3")
            name = name_el.inner_text().strip() if name_el else ""
            if not name:
                lines = full_text.split("\n")
                name = lines[0].strip() if lines else ""
            name = clean_name(name)
            if not name or len(name) < 3 or any(w in name.lower() for w in SKIP_WORDS):
                continue

            addr_el = card.query_selector(".info-card__address, [class*='address'], [class*='city']")
            address = addr_el.inner_text().strip() if addr_el else ""
            if not address:
                for line in full_text.split("\n"):
                    if ADDR_RE.search(line.strip()):
                        address = line.strip()
                        break

            phones = []
            for pe in card.query_selector_all("span.search-itm__phone-item, li.list-menu-item--readonly span"):
                p = pe.inner_text().strip()
                if re.match(r'^\d[\d\s]+$', p) and len(p) >= 6:
                    phones.append(p)

            website = ""
            web_el = card.query_selector("a[href*='http']:not([href*='paginegialle']):not([href*='facebook'])")
            if web_el:
                website = web_el.get_attribute("href", "") or ""

            results.append({
                "nome": name[:120],
                "indirizzo": address,
                "telefono": ", ".join(phones[:3]) if phones else "",
                "sito": website,
            })
        except:
            continue
    return results


# ── SOURCE 1: PAGINEGIALLE ────────────────────────────────────
def scrape_paginegialle(ctx):
    all_r = []
    seen = set()
    total = 0
    for cat, q in CATEGORIES:
        for city in CITIES:
            url = f"https://www.paginegialle.it/ricerca/{q}/{city.lower().replace(' ', '%20')}"
            page = None
            try:
                page = ctx.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(2.5)
                for sel in ["button:has-text('Accetta')", "#onetrust-accept-btn-handler"]:
                    try: page.click(sel, timeout=1000)
                    except: pass

                # Pagination: click "Mostra altri risultati" up to 5 times
                for _ in range(5):
                    page.evaluate("window.scrollBy(0, 1500)")
                    time.sleep(0.4)
                    try:
                        btn = page.query_selector("div.listing__showmore, button:has-text('Mostra altri'), a:has-text('Mostra altri')")
                        if btn:
                            btn.click()
                            time.sleep(1.5)
                    except:
                        break

                cards = extract_cards_pg(page)
                for c in cards:
                    c["categoria"] = cat
                    c["citta"] = city
                    c["fonte"] = "PagineGialle"
                    c["descrizione"] = ""
                    c["note"] = ""
                    key = (c["nome"].lower(), c["indirizzo"].lower())
                    if key not in seen:
                        seen.add(key)
                        all_r.append(c)
                        total += 1
                page.close()
            except Exception as e:
                try: page.close()
                except: pass
            if total % 50 < len(cards):
                print(f"  [{cat}] {city}: +{len(cards)} (tot: {total})", flush=True)
    return all_r


# ── SOURCE 2: GOOGLE MAPS ──────────────────────────────────────
def extract_cards_gmaps(page):
    """Extract business cards from Google Maps search results."""
    results = []
    for _ in range(3):
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(0.6)
    time.sleep(1.5)
    
    cards = page.query_selector_all("div[role='article'], div[role='feed'] > div, a[href*='/place/']")
    if not cards:
        cards = page.query_selector_all("div.Nv2PK, div[jsaction*='mouseover']")
    
    for card in cards[:40]:
        try:
            text = card.inner_text().strip()
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if len(lines) < 2:
                continue
            
            name = lines[0]
            name = clean_name(name)
            if not name or len(name) < 3:
                continue
            
            address = ""
            phone = ""
            website = ""
            
            for line in lines[1:]:
                lc = line.lower()
                if not address and (any(kw in lc for kw in ['via ', 'piazza ', 'corso ', 'viale ']) or re.search(r'\d{4,5}\s+\w{2}', line)):
                    address = line
                elif not phone and re.search(r'[\d\s]{8,}', line) and not re.match(r'\d+ recensioni?', lc):
                    phone = line
                elif not website and ('.it' in line or '.com' in line):
                    website = line
            
            rating = ""
            for line in lines:
                m = re.search(r'(\d[.,]\d)\s*\((\d+)\)', line)
                if m:
                    rating = f"{m.group(1)} ({m.group(2)} reviews)"
                    break
            
            results.append({
                "nome": name[:120],
                "indirizzo": address,
                "telefono": phone,
                "sito": website,
                "note": rating,
            })
        except:
            continue
    return results


def scrape_gmaps(ctx):
    """Scrape Google Maps for businesses in target area."""
    all_r = []
    seen = set()
    total = 0
    
    for cat, q in CATEGORIES:
        for city in ["Varese", "Como", "Gallarate", "Busto Arsizio", "Verbania"]:
            page = None
            try:
                page = ctx.new_page()
                search_url = f"https://www.google.com/maps/search/{q}+{city}/?hl=it"
                page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(4)
                
                # Dismiss cookie
                try: page.click("button:has-text('Accetta tutto'), button:has-text('Accetta')", timeout=2000)
                except: pass
                
                time.sleep(1)
                
                # Scroll results sidebar
                for _ in range(4):
                    page.keyboard.press("PageDown")
                    time.sleep(0.3)
                
                cards = extract_cards_gmaps(page)
                for c in cards:
                    c["categoria"] = cat
                    c["citta"] = city
                    c["fonte"] = "GoogleMaps"
                    c["descrizione"] = ""
                    key = (c["nome"].lower(), c["indirizzo"].lower())
                    if key not in seen:
                        seen.add(key)
                        all_r.append(c)
                        total += 1
                page.close()
                print(f"  [GMaps] {cat} {city}: +{len(cards)} (tot: {total})", flush=True)
            except Exception as e:
                try: page.close()
                except: pass
                print(f"  [GMaps] {cat} {city}: ERR {str(e)[:60]}", flush=True)
    return all_r


# ── MAIN ───────────────────────────────────────────────────────
print("=" * 60, flush=True)
print("Multi-Source B2B Scraper — M&M Energy", flush=True)
print("Sources: PagineGialle, Google Maps", flush=True)
print(f"Cities: {len(CITIES)}  |  Categories: {len(CATEGORIES)}", flush=True)
print("=" * 60, flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="it-IT",
        viewport={"width": 1920, "height": 1080},
    )
    
    print("\n--- PAGINEGIALLE ---", flush=True)
    pg_results = scrape_paginegialle(ctx)
    print(f"PagineGialle: {len(pg_results)} total", flush=True)
    
    print("\n--- GOOGLE MAPS ---", flush=True)
    gm_results = scrape_gmaps(ctx)
    print(f"Google Maps: {len(gm_results)} total", flush=True)
    
    browser.close()

# ── MERGE & DEDUP ──────────────────────────────────────────────
all_contacts = {}
for r in pg_results + gm_results:
    key = (r["nome"].lower(), r.get("indirizzo", "").lower())
    if key in all_contacts:
        existing = all_contacts[key]
        if r["telefono"] and not existing["telefono"]:
            existing["telefono"] = r["telefono"]
        if r["sito"] and not existing["sito"]:
            existing["sito"] = r["sito"]
        if r["note"] and not existing["note"]:
            existing["note"] = r["note"]
        existing["fonte"] = existing["fonte"] + "+" + r["fonte"]
    else:
        all_contacts[key] = r

merged = list(all_contacts.values())

with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["categoria","citta","fonte","nome","indirizzo","telefono","sito","descrizione","note"])
    w.writeheader()
    w.writerows(merged)

with_phone = sum(1 for r in merged if r["telefono"].strip())
with_web = sum(1 for r in merged if r["sito"].strip())
print(f"\n{'='*60}", flush=True)
print(f"FINAL CSV: {len(merged)} contatti totali", flush=True)
print(f"  With phone: {with_phone} ({100*with_phone//max(len(merged),1)}%)", flush=True)
print(f"  With website: {with_web} ({100*with_web//max(len(merged),1)}%)", flush=True)
src_counts = Counter(r["fonte"] for r in merged)
for src, n in src_counts.most_common():
    print(f"  {src}: {n}", flush=True)
cat_counts = Counter(r["categoria"] for r in merged)
for cat, n in cat_counts.most_common():
    print(f"  {cat}: {n}", flush=True)
