"""FASE 4 v3: Generate structured profiles + scores from full site texts."""
import csv, json, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = r"C:\Users\marco\Projects\consulenza_energy"
CSV_PATH = os.path.join(BASE, "data", "contatti_b2b.csv")
JSON_PATH = os.path.join(BASE, "data", "site_texts.json")

with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    all_rows = list(csv.DictReader(f))

with open(JSON_PATH, "r", encoding="utf-8") as f:
    site_texts = json.load(f)

print(f"Contacts: {len(all_rows)} | Site texts: {len(site_texts)}")

# ── SCORING ENGINE ──────────────────────────────────────────────

# Category baseline score (energy consumption potential)
CAT_BASELINE = {
    "Ristoranti/Pizzerie": 9,
    "Hotel/B&B": 8,
    "Palestre": 7,
    "Officine/Artigiani": 6,
    "Lavanderie": 7,
}

# High-energy keywords (raise score)
ENERGY_KW = {
    "forno": 1, "cucina": 1, "cella frigo": 1, "frigorifero": 1, "refrigerazione": 1,
    "climatizzatore": 1, "aria condizionata": 1, "condizionamento": 1, "hvac": 1,
    "caldaia": 1, "riscaldamento": 1, "pompa di calore": 1, "pdc": 1,
    "piscina": 1, "sauna": 1, "bagno turco": 1, "spa": 1,
    "lavatrice": 1, "asciugatrice": 1, "lavaggio industriale": 1, "tintoria": 1,
    "compressore": 1, "tornio": 1, "fresa": 1, "saldatrice": 1,
    "illuminazione": 1, "led": 1, " lampada": 1,
    "camera": 0.5, "suite": 0.5, "stanza": 0.5, "coperto": 0.5,
}

# Low-energy / micro business keywords (lower score)
LOW_KW = {
    "freelance": -2, "libero professionista": -2, "consulenza": -1,
    "personal trainer": -1, "pt ": -1, "coach online": -1,
    "domicilio": -1, "a casa": -1, "one person": -2, "solo": -1,
    "studio privato": -1, "ufficio": -1, "coworking": -1,
}

def safe_text(site_data):
    if not site_data:
        return ""
    title = site_data.get("title", "")
    meta = site_data.get("meta", "")
    text = site_data.get("text", "")
    return f"{title} {meta} {text}".lower()

def analyze(r, site_data):
    cat = r["categoria"]
    name = r["nome"]
    full_text = safe_text(site_data)
    
    if not full_text:
        return {
            "descrizione": "Nessuna informazione disponibile dal sito web",
            "punteggio": CAT_BASELINE.get(cat, 5),
            "note": "",
        }
    
    # Score calculation
    score = CAT_BASELINE.get(cat, 5)
    
    # Add for energy keywords
    energy_hits = []
    for kw, pts in ENERGY_KW.items():
        if kw in full_text:
            energy_hits.append(kw)
            score += pts
    
    # Subtract for low-energy indicators
    low_hits = []
    for kw, pts in LOW_KW.items():
        if kw in full_text:
            low_hits.append(kw)
            score += pts
    
    # Normalize to 1-10
    score = max(1, min(10, round(score)))
    
    # Build description
    title = site_data.get("title", "") if site_data else ""
    meta = site_data.get("meta", "") if site_data else ""
    text = site_data.get("text", "") if site_data else ""
    
    # Clean text: remove excess whitespace
    clean_text = re.sub(r'\s+', ' ', (meta + " " + text)[:800]).strip()
    
    # Build call suggestions based on energy keywords found
    sugg = []
    if any(kw in full_text for kw in ["forno", "cucina", "cella frigo", "frigorifero"]):
        sugg.append("Menzionare risparmio su refrigerazione e cottura")
    if any(kw in full_text for kw in ["climatizzatore", "aria condizionata", "condizionamento", "hvac"]):
        sugg.append("Focus su efficientamento climatizzazione")
    if any(kw in full_text for kw in ["caldaia", "riscaldamento", "pompa di calore"]):
        sugg.append("Proporre check caldaia/impianto termico")
    if any(kw in full_text for kw in ["piscina", "sauna", "spa"]):
        sugg.append("Evidenziare costi energetici piscina/spa/wellness")
    if any(kw in full_text for kw in ["lavatrice", "asciugatrice", "lavaggio industriale"]):
        sugg.append("Ottimizzazione ciclo lavaggio e asciugatura")
    if any(kw in full_text for kw in ["compressore", "tornio", "fresa", "saldatrice"]):
        sugg.append("Analisi consumi macchinari e rifasamento")
    if any(kw in full_text for kw in ["illuminazione", "led", "lampada"]):
        sugg.append("Relamping LED con payback 8-12 mesi")
    if any(kw in full_text for kw in ["camera", "suite", "stanza"]):
        sugg.append("Chiave magnetica spegni-tutto per camere")
    
    if not sugg:
        sugg.append("Check energetico completo con termocamera")
    
    # Build structured profile
    profilo = (
        f"[{title[:120]}] "
        f"{clean_text[:500]}"
    )
    
    if sugg:
        profilo += " | SUGGERIMENTI: " + "; ".join(sugg)
    
    note = ""
    if energy_hits:
        note = f"Consumi: {', '.join(energy_hits[:5])}"
    
    return {
        "descrizione": profilo[:3000],
        "punteggio": score,
        "note": note,
    }

# ── PROCESS ────────────────────────────────────────────────────
enriched = 0
removed = 0
kept = []

for i, r in enumerate(all_rows):
    site = r.get("sito", "").strip()
    phone = r.get("telefono", "").strip()
    
    # Remove: no phone AND no website
    if not phone and not site:
        removed += 1
        continue
    
    # If no site, keep as-is with baseline score
    if not site.startswith("http"):
        r["punteggio"] = str(CAT_BASELINE.get(r["categoria"], 5))
        kept.append(r)
        continue
    
    # Analyze site
    data = site_texts.get(str(i))
    if data:
        profile = analyze(r, data)
        r["descrizione"] = profile["descrizione"]
        r["punteggio"] = str(profile["punteggio"])
        if "note" in profile and profile["note"]:
            r["note"] = profile["note"]
        enriched += 1
    else:
        r["descrizione"] = "[SITO NON RAGGIUNGIBILE]"
        r["punteggio"] = str(CAT_BASELINE.get(r["categoria"], 5))
    
    kept.append(r)

# Save with new columns
out_path = os.path.join(BASE, "data", "contatti_b2b.csv")
tmp_path = os.path.join(BASE, "data", "contatti_enriched.csv")
fieldnames = ["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note","punteggio"]
with open(tmp_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    w.writerows(kept)

# ── REPORT ─────────────────────────────────────────────────────
print(f"\nFASE 4 v3 COMPLETA")
print(f"  Rimosse (no tel + no web): {removed}")
print(f"  Inserite: {len(kept)}")
print(f"  Profili generati: {enriched}")

scores = [int(r["punteggio"]) for r in kept if r.get("punteggio", "").isdigit()]
if scores:
    print(f"  Score medio: {sum(scores)/len(scores):.1f}")
    for s, n in Counter(scores).most_common():
        bar = "█" * n
        print(f"    {s:>2}: {bar} ({n})")

# Category breakdown
cat_counts = Counter(r["categoria"] for r in kept)
for c, n in cat_counts.most_common():
    ph = sum(1 for r in kept if r["categoria"]==c and r["telefono"].strip())
    wb = sum(1 for r in kept if r["categoria"]==c and r["sito"].strip().startswith("http"))
    desc = sum(1 for r in kept if r["categoria"]==c and r["descrizione"].strip() and "[SITO NON" not in r["descrizione"] and "Nessuna informazione" not in r["descrizione"])
    print(f"  {c}: {n} (tel:{ph} web:{wb} desc:{desc})")
