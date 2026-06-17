"""
PagineGialle PROPER scraper — extracts from search results page directly.
Phone numbers are already visible in SPAN.search-itm__phone-item.
"""
import csv, time, re, os
from playwright.sync_api import sync_playwright

BASE = r"C:\Users\marco\Projects\consulenza_energy"
OUTPUT = os.path.join(BASE, "contatti_b2b.csv")

SEARCHES = [
    ("Ristoranti/Pizzerie", "ristoranti", "Varese"),
    ("Ristoranti/Pizzerie", "ristoranti", "Como"),
    ("Ristoranti/Pizzerie", "ristoranti", "Gallarate"),
    ("Ristoranti/Pizzerie", "ristoranti", "Busto Arsizio"),
    ("Palestre", "palestre", "Varese"),
    ("Palestre", "palestre", "Como"),
    ("Palestre", "palestre", "Gallarate"),
    ("Officine/Artigiani", "officine meccaniche", "Varese"),
    ("Officine/Artigiani", "officine meccaniche", "Como"),
    ("Lavanderie", "lavanderie industriali", "Varese"),
    ("Lavanderie", "lavanderie industriali", "Como"),
    ("Hotel/B&B", "hotel", "Como"),
    ("Hotel/B&B", "hotel", "Varese"),
    ("Hotel/B&B", "hotel", "Verbania"),
]

ADDR_RE = re.compile(
    r"(Via|Piazza|Corso|Viale|Largo|Localit[aà]|Strada|Contrada)\s+.+,\s*\d+\s*[-–]\s*\d{4,5}\s*\S+"
)
SKIP_NAMES = {"vedi", "prenota", "mostra", "attiva", "categoria", "ordina per", "servizi in",
              "tipi di", "quartiere", "filtra", "rilevanza", "nuovo", "distanza", "popolarit",
              "risultati fuori", "paginegialle", "accedi", "registra", "cerca per"}


def extract_cards(page):
    """Extract business cards from PagineGialle search results."""
    results = []
    
    # Primary: cards in main listing
    cards = page.query_selector_all("div.search-itm.card-listing, div.card-azienda")
    
    for card in cards:
        try:
            full_text = card.inner_text()
            
            # Get name from info-card__title or first meaningful line
            name_el = card.query_selector(".info-card__title, h2, h3")
            name = name_el.inner_text().strip() if name_el else ""
            if not name:
                lines = full_text.split("\n")
                name = lines[0].strip() if lines else ""
            
            # Clean name: remove review count like "(145)", distance like "5.1km"
            name = re.sub(r'\s*\(\d+\)\s*$', '', name)
            name = re.sub(r'\s*\d+\.?\d*km$', '', name, flags=re.IGNORECASE)
            name = re.sub(r'\s*Suggerito\s*$', '', name)
            
            if not name or len(name) < 3:
                continue
            if any(w in name.lower() for w in SKIP_NAMES):
                continue
            
            # Get address
            addr_el = card.query_selector(".info-card__address, [class*='address'], [class*='city']")
            address = addr_el.inner_text().strip() if addr_el else ""
            if not address:
                for line in full_text.split("\n"):
                    line = line.strip()
                    if ADDR_RE.search(line):
                        address = line
                        break
            
            # Get phones (all visible numbers)
            phones = []
            phone_els = card.query_selector_all("span.search-itm__phone-item, li.list-menu-item--readonly span")
            for pe in phone_els:
                ptext = pe.inner_text().strip()
                if re.match(r'^\d[\d\s]+$', ptext) and len(ptext) >= 6:
                    phones.append(ptext)
            
            phone = ", ".join(phones[:3]) if phones else ""
            
            results.append({
                "nome": name[:120],
                "indirizzo": address,
                "telefono": phone,
            })
        except:
            continue
    
    # Secondary: carousel items (TheFork sponsored)
    carousel_cards = page.query_selector_all("li.listing-category-itm, div.listing-carousel__item")
    for card in carousel_cards:
        try:
            title_el = card.query_selector("h3")
            if not title_el:
                continue
            name = title_el.inner_text().strip()
            name = re.sub(r'\s*\|\s*\S+$', '', name)  # Remove "| Varese" suffix
            
            addr_el = card.query_selector("[class*='address'], [class*='city']")
            address = addr_el.inner_text().strip() if addr_el else ""
            
            if name and len(name) > 2 and not any(w in name.lower() for w in SKIP_NAMES):
                results.append({
                    "nome": name[:120],
                    "indirizzo": address,
                    "telefono": "",
                })
        except:
            continue
    
    return results


def scrape_search(ctx, categoria, query, citta):
    url = f"https://www.paginegialle.it/ricerca/{query}/{citta.lower().replace(' ', '%20')}"
    page = ctx.new_page()
    results = []
    
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        
        # Dismiss cookie
        for sel in ["button:has-text('Accetta')", "#onetrust-accept-btn-handler"]:
            try:
                page.click(sel, timeout=1500)
            except:
                pass
        
        # Scroll to load more
        for _ in range(6):
            page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(0.5)
        
        cards = extract_cards(page)
        
        # De-duplicate within this search
        seen_names = set()
        for c in cards:
            key = c["nome"].lower()
            if key not in seen_names:
                seen_names.add(key)
                c["categoria"] = categoria
                c["citta"] = citta
                c["sito"] = ""
                c["descrizione"] = ""
                c["note"] = ""
                results.append(c)
        
    except Exception as e:
        print(f"  ERR: {e}", flush=True)
    finally:
        page.close()
    
    with_phone = sum(1 for r in results if r["telefono"])
    print(f"  -> {len(results)} results ({with_phone} with phone)", flush=True)
    return results


# ── MAIN ──
print("PagineGialle PROPER Scraper\n", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="it-IT",
        viewport={"width": 1920, "height": 1080},
    )
    
    all_results = []
    all_seen = set()
    
    for cat, q, city in SEARCHES:
        print(f"[{cat}] {city} ...", end=" ", flush=True)
        results = scrape_search(ctx, cat, q, city)
        
        new = 0
        for r in results:
            key = (r["nome"].lower(), r.get("indirizzo", ""))
            if key not in all_seen:
                all_seen.add(key)
                all_results.append(r)
                new += 1
        
        print(f"    {new} new (total: {len(all_results)})", flush=True)
    
    browser.close()

# Save CSV
with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["categoria","citta","nome","indirizzo","telefono","sito","descrizione","note"])
    w.writeheader()
    w.writerows(all_results)

total_phone = sum(1 for r in all_results if r["telefono"].strip())
print(f"\nTOTALE: {len(all_results)} contatti ({total_phone} with phone) in {OUTPUT}")

from collections import Counter
for cat, n in Counter(r["categoria"] for r in all_results).most_common():
    print(f"  {cat}: {n}")
