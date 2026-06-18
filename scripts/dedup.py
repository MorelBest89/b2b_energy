"""Deduplicate contacts: PG-GM cross-source + internal duplicates."""
import csv, re
from difflib import SequenceMatcher
from collections import defaultdict

rows = list(csv.DictReader(open(r"C:\Users\marco\Projects\consulenza_energy\data\contatti_b2b.csv", "r", encoding="utf-8-sig")))

def extract_numbers(s):
    return re.sub(r'[^\d]', '', s)[:8]

# Group by normalized name for internal dedup
name_groups = defaultdict(list)
for i, r in enumerate(rows):
    key = r["nome"].strip().lower()
    key = re.sub(r'[\s\-\.]+', ' ', key)
    name_groups[key].append(i)

# Dedup within same source
removed = set()
for name, indices in name_groups.items():
    if len(indices) <= 1:
        continue
    
    # Group by source
    pg_indices = [i for i in indices if rows[i]["fonte"] == "PagineGialle"]
    gm_indices = [i for i in indices if rows[i]["fonte"] == "GoogleMaps"]
    
    # PG-GM cross-source: keep GM (better data with website), remove PG
    if pg_indices and gm_indices:
        for pi in pg_indices:
            r = rows[pi]
            pg_num = extract_numbers(r["indirizzo"])
            # Check if address numbers match
            for gi in gm_indices:
                g = rows[gi]
                gm_num = extract_numbers(g["indirizzo"])
                if pg_num == gm_num and len(pg_num) >= 6:
                    removed.add(pi)
                    # Enrich GM with PG phone if GM lacks
                    if not g["telefono"].strip() and r["telefono"].strip():
                        rows[gi]["telefono"] = r["telefono"]
                    break
        continue
    
    # Internal PG duplicates: keep one with most data
    if len(pg_indices) > 1:
        best = max(pg_indices, key=lambda i: (
            len(rows[i]["telefono"]), len(rows[i].get("sito", ""))
        ))
        for pi in pg_indices:
            if pi != best:
                removed.add(pi)
    
    # Internal GM duplicates: keep one with most data
    if len(gm_indices) > 1:
        best = max(gm_indices, key=lambda i: (
            len(rows[i]["telefono"]), len(rows[i].get("sito", ""))
        ))
        for gi in gm_indices:
            if gi != best:
                removed.add(gi)

# Cross-source fuzzy match for remaining (different name, same address)
print("Fuzzy cross-source matching...")
pg_remaining = [i for i in range(len(rows)) if rows[i]["fonte"] == "PagineGialle" and i not in removed]
gm_remaining = [i for i in range(len(rows)) if rows[i]["fonte"] == "GoogleMaps" and i not in removed]

fuzzy_removed = set()
for pi in pg_remaining:
    p = rows[pi]
    pn = p["nome"].lower().strip()
    pnum = extract_numbers(p["indirizzo"])
    for gi in gm_remaining:
        g = rows[gi]
        gn = g["nome"].lower().strip()
        gnum = extract_numbers(g["indirizzo"])
        
        name_sim = SequenceMatcher(None, pn, gn).ratio()
        if name_sim >= 0.65 and pnum == gnum and len(pnum) >= 6:
            fuzzy_removed.add(pi)
            if not g["telefono"].strip() and p["telefono"].strip():
                rows[gi]["telefono"] = p["telefono"]
            break

removed |= fuzzy_removed

# Keep non-removed
kept = [rows[i] for i in range(len(rows)) if i not in removed]

path = r"C:\Users\marco\Projects\consulenza_energy\data\contatti_b2b.csv"
with open(path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note"])
    w.writeheader()
    w.writerows(kept)

print(f"\nDeduplication report:")
print(f"  Input: {len(rows)}")
print(f"  Removed: {len(removed)} (exact: {sum(1 for i in removed if i not in fuzzy_removed)}, fuzzy: {len(fuzzy_removed)})")
print(f"  Output: {len(kept)}")
ph = sum(1 for r in kept if r["telefono"].strip())
wb = sum(1 for r in kept if r.get("sito", "").strip())
print(f"  Phone: {ph} ({100*ph//len(kept)}%)")
print(f"  Web: {wb} ({100*wb//len(kept)}%)")
