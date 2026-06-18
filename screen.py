"""FASE 1: Screening — remove garbage contacts from CSV."""
import csv, re, os
from collections import Counter

BASE = r"C:\Users\marco\Projects\consulenza_energy"
PATH = os.path.join(BASE, "contatti_b2b.csv")

# Load from original per-category sources (not already-screened CSV)
rows = []
srcs = {
    "contatti_ristoranti.csv": "Ristoranti/Pizzerie",
    "contatti_palestre.csv": "Palestre",
    "contatti_officine.csv": "Officine/Artigiani",
    "contatti_lavanderie.csv": "Lavanderie",
    "contatti_hotel.csv": "Hotel/B&B",
}
for fn, cat in srcs.items():
    path = os.path.join(BASE, fn)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                r["categoria"] = cat
                r.setdefault("fonte", "PagineGialle")
                r.setdefault("sito", "")
                r.setdefault("descrizione", "")
                r.setdefault("note", "")
                rows.append(r)
    else:
        print(f"WARNING: {fn} not found")

initial = len(rows)
print(f"Input: {initial} contacts")

# ── REJECTION RULES ──────────────────────────────────────────

REJECT_NAMES = {
    # UI labels from PagineGialle
    "whatsapp", "scrivici", "consegna a domicilio", "servizi per disabili",
    "tavoli all aperto", "parcheggio", "aria condizionata", "animali ammessi",
    "wifi", "wi-fi", "reception 24h", "hotel con ristorante",
    "telefono", "sito web", "indicazioni stradali", "prenota", "mostra numero",
    "chiama", "salva", "invia", "prenota un tavolo", "mostra altri risultati",
    "ordina per rilevanza", "ordina per distanza", "apre tra", "aperto fino",
    "chiuso", "aperto ora", "vedi su mappa", "mostra tutto",
    "alberghi e hotel", "ristoranti e trattorie", "pizzeria",
    "suggerito", "nuovo", "pubblicita", "annuncio",
    "carica altri", "categorie piu cercate", "cosa ti serve",
    "sei un azienda", "accedi", "registra azienda", "registrati",
    # Additional labels found in data
    "vedi tutti gli articoli", "vedi tutti", "auto sostitutiva",
    "guida michelin", "musica dal vivo", "karaoke", "area bimbi",
    "tavoli all'aperto", "asporto", "consegna", "cucina tipica",
    "cucina vegetariana", "cucina etnica", "senza glutine", "vegano",
    "prenota con thefork", "prenota con wheno",
    "accesso disabili", "carte di credito", "carta di credito",
    "pagamento contactless", "pagamento digitale",
    "consegna a domicilio gratuita",
}

REJECT_PREFIXES = (
    "via ", "piazza ", "corso ", "viale ", "largo ", "localit",
    "quartiere ", "comune di ", "provincia di ",
)

def should_reject(r):
    name = r["nome"].strip()
    nlower = name.lower().rstrip(".")
    addr = r["indirizzo"].strip()
    
    # 1. Empty name
    if not name:
        return "EMPTY_NAME"
    
    # 2. Name is exactly a reject label
    if nlower in REJECT_NAMES:
        return "REJECT_LABEL"
    
    # 3. Name is very short and no phone (likely garbage)
    if len(name) < 4 and not r["telefono"].strip():
        return "SHORT_NAME_NO_PHONE"
    
    # 4. Short name + one of the generic tags
    if len(name) < 8 and nlower in {"spa", "piscina", "bar", "wifi", "giardino", "palestra"}:
        return "SERVICE_TAG"
    
    # 5. Name starts with address pattern
    if nlower.startswith(REJECT_PREFIXES):
        return "NAME_IS_ADDRESS"
    
    # 6. Name matches address
    if nlower == addr.lower().rstrip("."):
        return "NAME_EQ_ADDRESS"
    
    # 7. Name contains category headers  
    for kw in ["ristoranti a ", "alberghi a ", "palestre a ", "officine a ",
               "piu di ", "risultati", "pagine gialle"]:
        if kw in nlower:
            return "CATEGORY_HEADER"
    
    # 8. Name is ALL CAPS and > 40 chars (likely a description)
    if name.isupper() and len(name) > 40:
        return "ALL_CAPS_DESC"
    
    # 9. Name ends with " (VA)" or " (CO)" = business name already has city tag baked in
    #    This is fine for now, skip
    
    return None


# ── EXECUTE ──────────────────────────────────────────────────
kept = []
removed = []
reasons = Counter()

for r in rows:
    reason = should_reject(r)
    if reason:
        reasons[reason] += 1
        removed.append((reason, r))
    else:
        kept.append(r)

# Save cleaned CSV
with open(PATH, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note"])
    w.writeheader()
    w.writerows(kept)

# ── REPORT ───────────────────────────────────────────────────
print(f"\n{'='*60}")
print("FASE 1 — SCREENING REPORT")
print(f"{'='*60}")
print(f"Input:          {initial:>6}")
print(f"Rimossi:        {len(removed):>6}  ({100*len(removed)//initial}%)")
print(f"Output:         {len(kept):>6}")
print(f"\nPer motivo:")
for reason, count in reasons.most_common():
    print(f"  {reason:<25} {count:>4}")

# Show samples of removed
print(f"\nCampioni rimossi:")
for reason in dict(reasons.most_common(5)):
    samples = [r for rsn, r in removed if rsn == reason][:3]
    print(f"\n--- {reason} ({reasons[reason]}) ---")
    for r in samples:
        print(f"  '{r['nome'][:60]}' | {r['citta']} | {r['categoria']}")

# Final stats
ph_before = sum(1 for r in rows if r["telefono"].strip())
ph_after = sum(1 for r in kept if r["telefono"].strip())
print(f"\nTelefoni: {ph_before} -> {ph_after} (-{ph_before - ph_after})")
print(f"Coverage: {100*ph_after//len(kept)}%")

bk = Counter(r["categoria"] for r in kept)
print(f"\nPer categoria:")
for c, n in bk.most_common():
    p = sum(1 for r in kept if r["categoria"]==c and r["telefono"].strip())
    print(f"  {c}: {n} (ph:{p})")
