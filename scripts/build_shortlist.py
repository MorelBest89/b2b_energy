"""Create shortlist.csv: top 30 per category, min score 6."""
import csv, os

BASE = r"C:\Users\marco\Projects\consulenza_energy"

with open(os.path.join(BASE, "data", "contatti_final.csv"), "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

categories = ["Ristoranti/Pizzerie","Hotel/B&B","Palestre","Officine/Artigiani","Lavanderie"]
MIN_SCORE = 6
TOP_N = 30

shortlist = []
cat_counts = {}

for cat in categories:
    cat_rows = [r for r in rows if r["categoria"] == cat and r["punteggio"].isdigit() and int(r["punteggio"]) >= MIN_SCORE]
    cat_rows.sort(key=lambda r: -int(r["punteggio"]))
    take = min(TOP_N, len(cat_rows))
    selected = cat_rows[:take]
    shortlist.extend(selected)
    cat_counts[cat] = take

print(f"Shortlist generata: {len(shortlist)} contatti")
for cat, n in cat_counts.items():
    print(f"  {cat}: {n} (min score: 6)")

fieldnames = ["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note","punteggio"]
with open(os.path.join(BASE, "data", "shortlist.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    w.writerows(shortlist)

print(f"Salvato: data/shortlist.csv")
