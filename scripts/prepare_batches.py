"""Prepare batch files for LLM profile generation."""
import csv, json, os, math

BASE = r"C:\Users\marco\Projects\consulenza_energy"

# Load current CSV
with open(os.path.join(BASE, "data", "contatti_b2b.csv"), "r", encoding="utf-8-sig") as f:
    all_rows = list(csv.DictReader(f))

# Load site texts
with open(os.path.join(BASE, "data", "site_texts.json"), "r", encoding="utf-8") as f:
    site_texts = json.load(f)

# Build list of contacts WITH site texts
contacts = []
for i, r in enumerate(all_rows):
    sidx = str(i)
    if sidx in site_texts and r.get("sito","").strip().startswith("http"):
        d = site_texts[sidx]
        contacts.append({
            "index": i,
            "nome": r["nome"],
            "citta": r["citta"],
            "categoria": r["categoria"],
            "telefono": r.get("telefono",""),
            "sito": r.get("sito",""),
            "title": d.get("title",""),
            "meta": d.get("meta",""),
            "text": d.get("text","")[:3000],  # Limit text per token budget
        })

# Also collect contacts WITHOUT site texts (for baseline scoring)
no_site = []
for i, r in enumerate(all_rows):
    if not r.get("sito","").strip().startswith("http"):
        no_site.append(i)

print(f"Contacts WITH site text: {len(contacts)}")
print(f"Contacts WITHOUT site text: {len(no_site)}")

# Split into batches of 50
BATCH_SIZE = 50
batches = [contacts[i:i+BATCH_SIZE] for i in range(0, len(contacts), BATCH_SIZE)]
print(f"Batches: {len(batches)}")

outdir = os.path.join(BASE, "data", "batches")
os.makedirs(outdir, exist_ok=True)

for idx, batch in enumerate(batches):
    path = os.path.join(outdir, f"batch_{idx}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False)
    print(f"  batch_{idx}.json: {len(batch)} contacts")

# Save contacts without site as baseline
baseline_path = os.path.join(BASE, "data", "batches", "baseline.json")
with open(baseline_path, "w", encoding="utf-8") as f:
    json.dump(no_site, f, ensure_ascii=False)
print(f"\nbaseline.json (no-site): {len(no_site)} contacts")
print(f"\nTotal to process: {len(contacts)} with site + {len(no_site)} without = {len(contacts)+len(no_site)}")
