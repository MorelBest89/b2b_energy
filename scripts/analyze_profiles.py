"""FASE 4 v4: AI-quality profiles from site analysis + refined scoring."""
import csv, json, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = r"C:\Users\marco\Projects\consulenza_energy"
JSON_PATH = os.path.join(BASE, "data", "site_texts.json")
CSV_IN = os.path.join(BASE, "data", "contatti_b2b.csv")
CSV_OUT = os.path.join(BASE, "data", "contatti_final.csv")

with open(CSV_IN, "r", encoding="utf-8-sig") as f:
    all_rows = list(csv.DictReader(f))

with open(JSON_PATH, "r", encoding="utf-8") as f:
    raw_sites = json.load(f)

site_texts = {}
for k, v in raw_sites.items():
    if v:
        site_texts[int(k)] = v

print(f"Contacts: {len(all_rows)} | Site texts: {len(site_texts)}")

# Map sites by URL: for each original index, look up the URL in the CURRENT CSV
# Then map URL -> data for matching
url_map = {}
for idx, data in site_texts.items():
    if idx < len(all_rows):
        row_url = all_rows[idx].get("sito", "").strip()
        if row_url:
            url_map[row_url] = data
    # Also try matching by name substring for edge cases
    if idx >= len(all_rows):
        # Index out of bounds: try to find by scanning smaller range
        for i, r in enumerate(all_rows):
            if r.get("sito","").strip() and data.get("title",""):
                # Check if row name appears in site title or vice versa
                rname = r["nome"].lower()[:20]
                stitle = data.get("title","").lower()
                if rname in stitle or stitle[:20] in rname:
                    url = r["sito"].strip()
                    if url and url not in url_map:
                        url_map[url] = data
                        break

print(f"URL map entries: {len(url_map)}")

def safe_text(data):
    if not data: return ""
    return f"{data.get('title','')} {data.get('meta','')} {data.get('text','')}".lower()

# ── BUSINESS TYPE DETECTION ─────────────────────────────────────
def detect_business_type(cat, text):
    """Detect specific business subtype from website text."""
    t = text.lower()
    if cat == "Ristoranti/Pizzerie":
        if "pizzeria" in t or "pizza" in t and "pizzeria" in t: return "pizzeria"
        if "kebab" in t: return "kebab/grill"
        if "sushi" in t or "giapponese" in t: return "ristorante giapponese"
        if "cinese" in t: return "ristorante cinese"
        if "steakhouse" in t or "grill" in t: return "steakhouse/grill"
        if "agriturismo" in t: return "agriturismo"
        if "bar" in t and "caffe" in t: return "bar/caffetteria"
        if "gelateria" in t or "gelato" in t: return "gelateria"
        return "ristorante"
    elif cat == "Hotel/B&B":
        if "5 stelle" in t or "lusso" in t: return "hotel di lusso"
        if "4 stelle" in t: return "hotel 4 stelle"
        if "3 stelle" in t: return "hotel 3 stelle"
        if "b&b" in t or "bed and breakfast" in t: return "bed & breakfast"
        if "agriturismo" in t: return "agriturismo"
        if "ostello" in t or "hostel" in t: return "ostello"
        return "hotel"
    elif cat == "Palestre":
        if "crossfit" in t: return "box crossfit"
        if "yoga" in t or "pilates" in t: return "studio yoga/pilates"
        if "piscina" in t: return "centro sportivo con piscina"
        if "personal" in t and "trainer" in t and "palestra" not in t: return "personal trainer"
        return "palestra"
    elif cat == "Officine/Artigiani":
        if "carrozzeria" in t: return "carrozzeria"
        if "gommista" in t or "pneumatici" in t: return "gommista"
        if "elettrauto" in t: return "elettrauto"
        if "meccanica di precisione" in t: return "meccanica di precisione"
        if "revisione" in t: return "centro revisioni"
        if "officina" in t: return "officina meccanica"
        return "officina"
    elif cat == "Lavanderie":
        if "industriale" in t: return "lavanderia industriale"
        if "tintoria" in t: return "tintoria"
        if "noleggio" in t: return "noleggio biancheria"
        return "lavanderia"
    return cat.lower()

# ── SIZE DETECTION ──────────────────────────────────────────────
def detect_size(text):
    """Detect business size from text."""
    t = text.lower()
    # Count rooms (hotels)
    rooms = re.findall(r'(\d+)\s*(camere?|stanze?|room)', t)
    if rooms:
        n = max(int(m[0]) for m in rooms)
        if n > 50: return "grande", n
        if n > 15: return "medio", n
        if n > 3: return "piccolo", n
    # Count seats (restaurants)
    seats = re.findall(r'(\d+)\s*(posti|coperti|persone)', t)
    if seats:
        n = max(int(m[0]) for m in seats)
        if n > 100: return "grande", n
        if n > 40: return "medio", n
        return "piccolo", n
    # Employees
    employees = re.findall(r'(\d+)\s*(dipendenti|collaboratori|addetti)', t)
    if employees:
        n = max(int(m[0]) for m in employees)
        if n > 20: return "grande", n
        if n > 5: return "medio", n
        return "piccolo", n
    # Multiple locations
    locs = re.findall(r'(\d+)\s*(sedi?|filiali|stabilimenti|punti vendita)', t)
    if locs and int(locs[0][0]) > 1:
        return "grande", int(locs[0][0])
    return "", 0

# ── ENERGY EQUIPMENT ────────────────────────────────────────────
def detect_energy(text):
    """Detect energy-relevant equipment and features."""
    t = text.lower()
    findings = {}
    if any(w in t for w in ["forno", "cucina", "cella frigo", "frigorifero", "abbattitore"]):
        findings["cucina"] = "attrezzatura cucina/refrigerazione"
    if any(w in t for w in ["piscina", "spa", "idromassaggio", "sauna", "bagno turco"]):
        findings["piscina/spa"] = "piscina e/o centro benessere"
    if any(w in t for w in ["climatizzatore", "aria condizionata", "condizionamento"]):
        findings["clima"] = "impianti di climatizzazione"
    if any(w in t for w in ["caldaia", "riscaldamento", "pompa di calore", "termico"]):
        findings["riscaldamento"] = "impianto termico/caldaia"
    if any(w in t for w in ["lavatrice", "asciugatrice", "lavaggio", "tintoria"]):
        findings["lavaggio"] = "macchinari lavaggio/asciugatura"
    if any(w in t for w in ["compressore", "tornio", "fresa", "saldatrice", "pressa"]):
        findings["macchinari"] = "macchinari industriali"
    if any(w in t for w in ["illuminazione", "led", "lampada", "neon"]):
        findings["luci"] = "impianto illuminazione"
    if any(w in t for w in ["camera", "suite", "stanza"]) and "Hotel" in text:
        findings["camere"] = "camere con gestione energetica"
    return findings

# ── IDENTIFY MICRO BUSINESS ────────────────────────────────────
def is_micro(text):
    t = text.lower()
    indicators = ["freelance", "libero professionista", "one person", "a domicilio",
                  "personal trainer", "personal training", "coach online",
                  "studio privato", "coworking", "un solo", "lavoro da casa",
                  "mi piace: ", "facebook", "segui", "iscriviti"]
    score = sum(1 for w in indicators if w in t)
    return score >= 2

# ── MAIN PROFILE GENERATOR ──────────────────────────────────────
def generate_profile(r, site_data):
    cat = r["categoria"]
    name = r["nome"]
    city = r["citta"]
    full_text = safe_text(site_data)
    
    btype = detect_business_type(cat, full_text)
    size, size_n = detect_size(full_text)
    energy = detect_energy(full_text if site_data else "")
    micro = is_micro(full_text)
    
    phone = r["telefono"].strip()
    website = r.get("sito", "").strip()
    has_phone = bool(phone)
    has_web = bool(website.startswith("http"))
    has_text = bool(full_text)
    
    # ── SCORE ──────────────────────────────────────────────────
    score = 0
    
    # Base: category fit (how well this category matches our ideal client)
    cat_score = {
        "Ristoranti/Pizzerie": 9,  # Max energy consumption (cooking + HVAC + refrigeration)
        "Hotel/B&B": 9,            # Max energy (rooms + restaurant + pool + common areas)
        "Palestre": 7,             # High (showers + HVAC + lighting)
        "Lavanderie": 7,           # High (washing machines + dryers)
        "Officine/Artigiani": 6,   # Medium (machinery, compressors)
    }
    score = cat_score.get(cat, 5)
    
    # Size adjustments
    if size == "grande": score = min(10, score + 1)
    elif size == "piccolo" and not energy: score = max(1, score - 1)
    
    # Energy equipment bonus
    if len(energy) >= 3: score = min(10, score + 1)
    elif len(energy) >= 1: score = min(10, score + 0.5)
    if not energy: score = max(1, score - 1)
    
    # Micro business penalty
    if micro: score = max(1, score - 3)
    
    # Data quality penalties
    if not has_text: score = max(1, score - 2)
    if not has_web: score = max(1, score - 1)
    if not has_phone: score = max(1, score - 1)
    
    score = max(1, min(10, round(score)))
    
    # ── DESCRIPTION ────────────────────────────────────────────
    if not has_text:
        desc = f"{name} e' un {btype} a {city}. {_no_info_note(cat)}"
        note = "Nessun sito web disponibile per analisi approfondita"
        return desc, score, note
    
    # Build rich description
    parts = []
    
    # 1. Who they are
    size_desc = ""
    if size == "grande": size_desc = "di grandi dimensioni"
    elif size == "medio": size_desc = "di medie dimensioni"
    
    a = "un'" if btype.startswith(("a","e","i","o")) else "un "
    parts.append(f"{name} e' {a}{btype} {size_desc}a {city}.")
    
    # 2. What they offer (from site analysis)
    site_text = site_data.get("text", "")
    meta = site_data.get("meta", "")
    
    # Extract key services from meta or first meaningful sentences
    services = []
    if meta:
        services.append(meta[:200])
    else:
        sentences = re.split(r'[.!?]+', site_text)
        for s in sentences[:5]:
            s = s.strip()
            if len(s) > 40 and not s.startswith(("cookie", "privacy", "policy")):
                services.append(s)
                if len(services) >= 2: break
    
    if services:
        parts.append("Offre: " + "; ".join(s[:120] for s in services[:2]) + ".")
    
    # 3. Energy-relevant equipment
    if energy:
        kit = ", ".join(list(energy.values())[:4])
        parts.append(f"Dispone di: {kit}.")
    
    # 4. How we can help (based on energy findings)
    help_text = _generate_help(energy, cat, btype, size, has_text)
    if help_text:
        parts.append(help_text)
    
    desc = " ".join(parts)[:2500]
    
    # ── NOTE (call suggestions) ────────────────────────────────
    suggestions = _generate_suggestions(energy, cat, btype)
    
    # Add data quality notes
    dq = []
    if not has_web: dq.append("SITO MANCANTE")
    if not has_phone: dq.append("TEL MANCANTE")
    if dq: suggestions.append("ATTENZIONE: " + ", ".join(dq))
    
    note = " | ".join(suggestions)[:500]
    
    return desc, score, note


def _no_info_note(cat):
    if cat in ("Ristoranti/Pizzerie", "Hotel/B&B"):
        return "Potenziale alto per check energetico (cucina, HVAC). Da contattare per verificare."
    return "Da contattare per verificare esigenze energetiche."

def _generate_help(energy, cat, btype, size, has_text):
    if not has_text: return ""
    if not energy: return "Potenziale da verificare con check energetico per identificare margini di risparmio."
    
    parts = []
    if "cucina" in energy:
        parts.append("riduzione costi energetici della cucina")
    if "clima" in energy:
        parts.append("efficientamento climatizzazione")
    if "riscaldamento" in energy:
        parts.append("verifica rendimento caldaia/impianto termico")
    if "piscina/spa" in energy:
        parts.append("abbattimento costi riscaldamento piscina/spa")
    if "camere" in energy:
        parts.append("gestione energetica camere (chiave magnetica, termostati)")
    if "luci" in energy:
        parts.append("relamping LED con payback 8-12 mesi")
    if "lavaggio" in energy:
        parts.append("ottimizzazione cicli lavaggio/asciugatura")
    if "macchinari" in energy:
        parts.append("analisi consumi macchinari e rifasamento")
    
    if parts:
        return f"M&M Energy puo' intervenire su: {', '.join(parts)}."
    return ""

def _generate_suggestions(energy, cat, btype):
    sugg = []
    if "cucina" in energy:
        sugg.append("Check consumi cucina (forni, celle frigo, abbattitori)")
    if "clima" in energy:
        sugg.append("Audit climatizzazione (split, canalizzati, pompe di calore)")
    if "piscina/spa" in energy:
        sugg.append("Costo energetico piscina/Spa: 30-50% della bolletta. Prioritario.")
    if "camere" in energy:
        sugg.append("Proporre chiave magnetica spegni-tutto per camere")
    if "luci" in energy:
        sugg.append("Relamping LED: si ripaga in meno di 12 mesi")
    if "riscaldamento" in energy:
        sugg.append("Verifica rendimento caldaia: se <80%, sostituzione paga da sola")
    if "macchinari" in energy:
        sugg.append("Rifasamento per eliminare penali energia reattiva")
    if "lavaggio" in energy:
        sugg.append("Ciclo lavaggio: ogni grado in meno = 5% risparmio energetico")
    
    if not sugg:
        sugg.append(f"Check energetico base con termocamera: identificare dispersioni e priorita' intervento")
    
    return sugg


# ── EXECUTE ─────────────────────────────────────────────────────
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
    
    data = None
    # Try URL match first (most reliable)
    if site.startswith("http") and site in url_map:
        data = url_map[site]
    # Fall back to index
    if not data:
        data = site_texts.get(i)
    desc, score, note = generate_profile(r, data)
    r["descrizione"] = desc
    r["punteggio"] = str(score)
    r["note"] = note
    
    if data:
        enriched += 1
    
    kept.append(r)

fieldnames = ["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note","punteggio"]
with open(CSV_OUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    w.writerows(kept)

# ── REPORT ─────────────────────────────────────────────────────
print(f"\nRimosse (no tel + no web): {removed}")
print(f"Inserite: {len(kept)}  |  Profili generati: {enriched}")

scores = [int(r["punteggio"]) for r in kept if r.get("punteggio", "").isdigit()]
if scores:
    print(f"Score medio: {sum(scores)/len(scores):.1f}")
    sc = Counter(scores)
    for s in range(10, 0, -1):
        n = sc.get(s, 0)
        bar = "█" * (n // 10)
        print(f"  {s:>2}: {bar} ({n})")

print()
for c in Counter(r["categoria"] for r in kept).most_common():
    cat = c[0]
    n = c[1]
    ph = sum(1 for r in kept if r["categoria"]==cat and r["telefono"].strip())
    wb = sum(1 for r in kept if r["categoria"]==cat and r["sito"].strip().startswith("http"))
    avg = sum(int(r["punteggio"]) for r in kept if r["categoria"]==cat and r.get("punteggio","").isdigit()) / max(1, n)
    print(f"  {cat}: {n}  tel:{ph}  web:{wb}  avg_score:{avg:.1f}")
