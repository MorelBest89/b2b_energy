"""Merge all batch results into the final CSV."""
import csv, json, os
from collections import Counter

BASE = r"C:\Users\marco\Projects\consulenza_energy"

# Load current CSV
with open(os.path.join(BASE, "data", "contatti_b2b.csv"), "r", encoding="utf-8-sig") as f:
    all_rows = list(csv.DictReader(f))

print(f"CSV rows: {len(all_rows)}")

# Load all result files
results_dir = os.path.join(BASE, "data", "batches")
merged = {}
for fn in sorted(os.listdir(results_dir)):
    if fn.startswith("result_") and fn.endswith(".json"):
        path = os.path.join(results_dir, fn)
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            n = len(data)
            merged.update(data)
            print(f"  {fn}: {n} contacts")
        except Exception as e:
            print(f"  {fn}: ERR {e}")

print(f"\nTotal results from LLM: {len(merged)}")

# Apply results to CSV
applied = 0
for i, r in enumerate(all_rows):
    sidx = str(i)
    if sidx in merged:
        profile = merged[sidx]
        r["descrizione"] = profile.get("descrizione", "")
        r["note"] = profile.get("note", "")
        r["punteggio"] = str(profile.get("punteggio", 5))
        applied += 1

print(f"Applied to CSV: {applied}")

# Baseline for contacts without site (no result)
for i, r in enumerate(all_rows):
    sidx = str(i)
    if sidx not in merged:
        cat = r["categoria"]
        has_phone = bool(r.get("telefono", "").strip())
        has_web = bool(r.get("sito", "").strip().startswith("http"))
        
        if not has_web and not has_phone:
            # Already removed in previous filtering - houldn't be here
            continue
        
        base_score = {"Ristoranti/Pizzerie": 5, "Hotel/B&B": 5, "Palestre": 4, "Officine/Artigiani": 4, "Lavanderie": 4}
        score = base_score.get(cat, 4)
        if not has_web: score = max(1, score - 1)
        if not has_phone: score = max(1, score - 1)
        
        r["descrizione"] = r.get("descrizione", "") or f"Sito web non disponibile per {r['nome']}. Contattare per verificare."
        r["punteggio"] = str(score)

# Save finale
out_path = os.path.join(BASE, "data", "contatti_final.csv")
fieldnames = ["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note","punteggio"]
with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    w.writerows(all_rows)

print(f"\nTOTALE FINALE: {len(all_rows)} contatti")

scores = [int(r["punteggio"]) for r in all_rows if r.get("punteggio","").isdigit()]
if scores:
    sc = Counter(scores)
    print(f"Score medio: {sum(scores)/len(scores):.1f}")
    for s in range(10, 0, -1):
        n = sc.get(s, 0)
        print(f"  {s:>2}: {n}")

ph = sum(1 for r in all_rows if r.get("telefono","").strip())
wb = sum(1 for r in all_rows if r.get("sito","").strip().startswith("http"))
desc = sum(1 for r in all_rows if r.get("descrizione","").strip() and len(r["descrizione"]) > 20)
print(f"\nPhone: {ph} | Web: {wb} | Descrizione: {desc}")
print(f"Saved: {out_path}")
