"""HOTEL fix: use 'alberghi' not 'hotel'. Incremental CSV saves."""
import csv, time, re, os
from playwright.sync_api import sync_playwright

BASE = r"C:\Users\marco\Projects\consulenza_energy"
OUTPUT = os.path.join(BASE, "data/contatti_hotel.csv")

CITIES = [
    "Varese", "Gallarate", "Busto Arsizio", "Saronno", "Tradate",
    "Malnate", "Luino", "Gavirate", "Somma Lombardo", "Cassano Magnago",
    "Como", "Cantu", "Erba", "Mariano Comense", "Olgiate Comasco",
    "Lomazzo", "Fino Mornasco", "Verbania", "Stresa", "Arona",
    "Laveno Mombello", "Angera",
]

ADDR_RE = re.compile(r"(Via|Piazza|Corso|Viale|Largo|Localit)")
PHONE_RE = re.compile(r'^[\d\s]+$')

SKIP_WORDS = {
    "vedi su mappa","prenota","mostra altri","attiva","categoria","ordina per",
    "servizi in","tipi di","quartiere","filtra","rilevanza","distanza","popolarit",
    "paginegialle","accedi","registra","mostra tutto","telefono","sito web",
    "indicazioni","chiama","salva","invia","pubblicita","annuncio","copernico",
    "apre tra","aperto fino","chiuso","aperto ora","suggerito","nuovo",
    "alberghi a","ristoranti a","in collaborazione","prenota con","scopri",
    "stelle","reception","parcheggio","hotel con","animali","wifi",
}
SKIP_NAMES = {
    "telefono", "sito web", "indicazioni stradali", "chiama", "salva", "invia",
    "prenota", "prenota un tavolo", "mostra numero", "mostra tutti",
}


def is_valid_name(s):
    s = s.strip()
    if not s or len(s) < 2 or len(s) > 120:
        return False
    slow = s.lower()
    if slow in SKIP_NAMES:
        return False
    # Reject lines that start with address patterns
    if slow.startswith(("via ", "piazza ", "corso ", "viale ", "largo ", "localit")):
        return False
    for w in SKIP_WORDS:
        if w in slow:
            return False
    if not re.search(r'[a-zA-Z]', s):
        return False
    return True


def clean_name(s):
    s = re.sub(r'\s*\(\d+\)\s*$', '', s)
    s = re.sub(r'\s*\d+\.?\d*km$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s*Suggerito\s*$', '', s)
    s = re.sub(r'\s*\|\s*\S+$', '', s)
    s = re.sub(r'^\d+\s*stella\s*$', '', s, flags=re.IGNORECASE)
    return s.strip()


def scrape(ctx, city):
    url = f"https://www.paginegialle.it/ricerca/alberghi/{city.lower().replace(' ', '%20')}"
    page = ctx.new_page()
    results = []
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(2.5)
        for sel in ["button:has-text('Accetta')", "#onetrust-accept-btn-handler"]:
            try: page.click(sel, timeout=1000)
            except: pass

        for _ in range(6):
            page.evaluate("window.scrollBy(0, 1200)")
            time.sleep(0.3)
            try:
                btn = page.query_selector("div.listing__showmore, button:has-text('Mostra altri'), a:has-text('Mostra altri')")
                if btn: btn.click(); time.sleep(1.3)
            except: break
        time.sleep(1)

        body = page.inner_text("body")
        lines = [l.strip() for l in body.split('\n') if l.strip()]

        # Collect phones by card position
        phones = {}
        for ps in page.query_selector_all("span.search-itm__phone-item"):
            try:
                ptext = ps.inner_text().strip()
                if PHONE_RE.match(ptext) and len(ptext) >= 6:
                    pid = ps.evaluate_handle(
                        "el=>{let p=el.closest('.search-itm,.card-azienda,.card-listing');return p?p.innerText.substring(0,60):''}"
                    )
                    k = str(pid)[:60] if pid else ""
                    if k: phones.setdefault(k[:50], []).append(ptext)
            except: pass

        i = 0
        while i < len(lines) - 1:
            line = lines[i]
            if not is_valid_name(line):
                i += 1; continue
            name = clean_name(line)
            if not name or len(name) < 2:
                i += 1; continue

            addr = ""; phone = ""; ai = i + 1
            for j in range(i + 1, min(i + 8, len(lines))):
                c = lines[j]
                # Address detection: starts with Via/Piazza/Corso etc. OR has CAP pattern
                if ADDR_RE.search(c) and len(c) > 10:
                    # Verify it looks like an address, not a business name
                    if re.match(r'(Via|Piazza|Corso|Viale|Largo|Localit)\s+.+\d{4,5}', c):
                        if not addr: addr = c; ai = j; break
                elif re.search(r'\d{5}\s+\w+\s*\([A-Z]{2}\)', c):
                    if not addr: addr = c; ai = j; break

            for pid, plist in phones.items():
                if name.lower()[:20] in pid.lower():
                    phone = ", ".join(plist[:3]); break

            if addr:
                results.append({
                    "fonte": "PagineGialle", "categoria": "Hotel/B&B",
                    "citta": city, "nome": name, "indirizzo": addr,
                    "telefono": phone, "sito": "", "descrizione": "", "note": "",
                })
                i = ai + 1
            else:
                i += 1
    except Exception as e:
        pass
    finally:
        page.close()
    return results


print(f"Hotel/B&B — 'alberghi' query — {len(CITIES)} cities", flush=True)
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="it-IT", viewport={"width": 1920, "height": 1080},
    )
    all_r = []; seen = set()
    for city in CITIES:
        print(f"  {city} ...", end=" ", flush=True)
        cards = scrape(ctx, city)
        added = 0
        for c in cards:
            k = (c["nome"].lower(), c["indirizzo"].lower())
            if k not in seen:
                seen.add(k); all_r.append(c); added += 1
        ph = sum(1 for c in cards if c["telefono"])
        print(f"+{added} (ph:{ph} tot:{len(all_r)})", flush=True)
        # Incremental save
        with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note"])
            w.writeheader(); w.writerows(all_r)
    browser.close()

ph_tot = sum(1 for r in all_r if r["telefono"].strip())
print(f"\nDONE: {len(all_r)} hotel (phone:{ph_tot}) -> {OUTPUT}", flush=True)
