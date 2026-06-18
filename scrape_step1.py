"""
PagGialle ALL CATEGORIES — step-by-step with card-level extraction.
Output: contatti_{categoria}.csv per ognuna delle 5 categorie.
"""
import csv, time, re, os
from collections import Counter
from playwright.sync_api import sync_playwright

BASE = r"C:\Users\marco\Projects\consulenza_energy"

CITIES = [
    "Varese", "Gallarate", "Busto Arsizio", "Saronno", "Tradate",
    "Malnate", "Luino", "Gavirate", "Somma Lombardo", "Cassano Magnago",
    "Como", "Cantu", "Erba", "Mariano Comense", "Olgiate Comasco",
    "Lomazzo", "Fino Mornasco", "Verbania", "Stresa", "Arona",
]

CATEGORIES = [
    ("ristoranti", "ristoranti"),
    ("palestre", "palestre"),
    ("officine", "officine meccaniche"),
    ("lavanderie", "lavanderie industriali"),
    ("hotel", "hotel"),
]

ADDR_RE = re.compile(r"(Via|Piazza|Corso|Viale|Largo|Localit)")
PHONE_RE = re.compile(r'^[\d\s]+$')

SKIP = {
    "vedi su mappa", "prenota", "mostra altri", "attiva", "categoria",
    "ordina per", "servizi in", "tipi di", "quartiere", "filtra", "rilevanza",
    "distanza", "popolarit", "paginegialle", "accedi", "registra",
    "mostra tutto", "telefono", "sito web", "indicazioni", "chiama",
    "salva", "invia", "in collaborazione", "prenota con", "scopri",
    "pubblicita", "annuncio", "apre tra", "aperto fino", "chiuso",
    "aperto ora", "suggerito", "nuovo", "ristoranti a", "ristoranti che",
    "palestre a", "officine a", "lavanderie a", "hotel a",
}


def filter_name(s):
    s = s.strip()
    if not s or len(s) < 3 or len(s) > 120:
        return False, ""
    for w in SKIP:
        if w in s.lower():
            return False, ""
    if not re.search(r'[a-zA-Z]', s):
        return False, ""
    # Clean name
    s = re.sub(r'\s*\(\d+\)\s*$', '', s)
    s = re.sub(r'\s*\d+\.?\d*km$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s*Suggerito\s*$', '', s)
    s = re.sub(r'\s*\|\s*\S+$', '', s)
    s = s.strip()
    return True, s


def scrape(ctx, cat_key, cat_label, city):
    url = f"https://www.paginegialle.it/ricerca/{cat_label}/{city.lower().replace(' ', '%20')}"
    page = ctx.new_page()
    results = []

    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        for sel in ["button:has-text('Accetta')", "#onetrust-accept-btn-handler"]:
            try:
                page.click(sel, timeout=1000)
            except:
                pass

        # Pagination
        for _ in range(5):
            page.evaluate("window.scrollBy(0, 1200)")
            time.sleep(0.3)
            try:
                btn = page.query_selector("div.listing__showmore, button:has-text('Mostra altri'), a:has-text('Mostra altri')")
                if btn:
                    btn.click()
                    time.sleep(1.5)
            except:
                break

        time.sleep(1)

        # Extract phone numbers with their parent cards
        phones_by_card = {}
        for ps in page.query_selector_all("span.search-itm__phone-item"):
            try:
                ptext = ps.inner_text().strip()
                if PHONE_RE.match(ptext) and len(ptext) >= 6:
                    parent = ps.evaluate_handle(
                        "el => { let p = el.closest('.search-itm, .card-azienda, .card-listing'); return p ? p.innerText.substring(0,80) : ''; }"
                    )
                    pid = str(parent) if parent else ""
                    if pid:
                        key = pid[:50]
                        if key not in phones_by_card:
                            phones_by_card[key] = []
                        phones_by_card[key].append(ptext)
            except:
                pass

        body = page.inner_text("body")
        lines = [l.strip() for l in body.split('\n') if l.strip()]

        i = 0
        while i < len(lines) - 1:
            line = lines[i]
            ok, name = filter_name(line)
            if not ok:
                i += 1
                continue

            # Find address + phone in next lines
            address = ""
            phone = ""
            addr_idx = i + 1

            for j in range(i + 1, min(i + 8, len(lines))):
                candidate = lines[j]
                # Is it an address?
                if ADDR_RE.search(candidate) and len(candidate) > 10 and not filter_name(candidate)[0]:
                    if not address:
                        address = candidate
                        addr_idx = j
                elif re.search(r'\d{5}\s+\w+', candidate):
                    if not address:
                        address = candidate
                        addr_idx = j
                if address:
                    break

            # Match phone
            for pid, plist in phones_by_card.items():
                if name.lower()[:20] in pid.lower():
                    phone = ", ".join(plist[:3])
                    break

            if address:
                results.append({
                    "fonte": "PagineGialle",
                    "categoria": cat_key,
                    "citta": city,
                    "nome": name[:120],
                    "indirizzo": address,
                    "telefono": phone,
                    "sito": "",
                    "descrizione": "",
                    "note": "",
                })
                i = addr_idx + 1
            else:
                i += 1

    except Exception as e:
        pass
    finally:
        page.close()

    return results


# ── MAIN ──
def run_category(cat_key, cat_label):
    outpath = os.path.join(BASE, f"contatti_{cat_key}.csv")
    print(f"\n{'='*60}")
    print(f"CATEGORY: {cat_key} ({len(CITIES)} cities)")
    print(f"{'='*60}", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="it-IT",
            viewport={"width": 1920, "height": 1080},
        )
        all_r = []
        seen = set()

        for city in CITIES:
            print(f"  {city} ...", end=" ", flush=True)
            cards = scrape(ctx, cat_key, cat_label, city)
            added = 0
            for c in cards:
                key = (c["nome"].lower(), c["indirizzo"].lower())
                if key not in seen:
                    seen.add(key)
                    all_r.append(c)
                    added += 1
            ph = sum(1 for c in cards if c["telefono"])
            print(f"+{added} (ph:{ph} tot:{len(all_r)})", flush=True)

        browser.close()

    with open(outpath, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note"])
        w.writeheader()
        w.writerows(all_r)

    ph_tot = sum(1 for r in all_r if r["telefono"].strip())
    print(f"\nSAVED: {len(all_r)} contacts (phone:{ph_tot}) -> {outpath}")
    return len(all_r)

# Run remaining categories only
run_category("lavanderie", "lavanderie industriali")
run_category("hotel", "hotel")
