"""Check duplicates between PagineGialle and Google Maps with fuzzy matching."""
import csv, re
from difflib import SequenceMatcher

rows = list(csv.DictReader(open(r"C:\Users\marco\Projects\consulenza_energy\data\contatti_b2b.csv", "r", encoding="utf-8-sig")))

pg = [r for r in rows if r["fonte"] == "PagineGialle"]
gm = [r for r in rows if r["fonte"] == "GoogleMaps"]
print(f"PG: {len(pg)} | GM: {len(gm)} | Total: {len(rows)}")

def extract_numbers(s):
    """Extract digits from string for address comparison."""
    return re.sub(r'[^\d]', '', s)

def fuzzy_match(a, b, threshold=0.70):
    return SequenceMatcher(None, a, b).ratio() >= threshold

matches = []
for p in pg:
    pn = p["nome"].lower().strip()
    pa = extract_numbers(p["indirizzo"])[:8]  # Compare CAP/house number
    for g in gm:
        gn = g["nome"].lower().strip()
        ga = extract_numbers(g["indirizzo"])[:8]
        
        name_match = fuzzy_match(pn, gn, 0.65)
        # Address: compare numeric parts (CAP + house number)
        addr_match = (pa == ga and len(pa) >= 6)
        
        if name_match and addr_match:
            matches.append((p, g))
            break

print(f"\nPotential duplicates: {len(matches)}")
print("Samples:")
for p, g in matches[:10]:
    print(f"  PG: {p['nome'][:40]} | {p['indirizzo'][:40]}")
    print(f"  GM: {g['nome'][:40]} | {g['indirizzo'][:40]}")
    print()

# Also check exact name duplicates within same source
from collections import Counter
pg_names = Counter(r["nome"].strip().lower() for r in pg)
gm_names = Counter(r["nome"].strip().lower() for r in gm)
pg_dupes = {k: v for k, v in pg_names.items() if v > 1}
gm_dupes = {k: v for k, v in gm_names.items() if v > 1}
print(f"Exact name dupes PG: {len(pg_dupes)} | GM: {len(gm_dupes)}")
