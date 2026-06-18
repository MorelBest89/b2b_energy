"""Enrich ALL PagineGialle contacts via Google Places API."""
import csv, httpx, time, os
from dotenv import load_dotenv

BASE = r"C:\Users\marco\Projects\consulenza_energy"
load_dotenv(os.path.join(BASE, ".env"))
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

CSV_PATH = os.path.join(BASE, "data", "contatti_b2b.csv")

with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    all_rows = list(csv.DictReader(f))

# Find PG contacts without website
to_enrich = [i for i, r in enumerate(all_rows) if r["fonte"] == "PagineGialle" and not r.get("sito", "").strip()]
print(f"PG contacts without site: {len(to_enrich)}")

HEADERS = {
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "places.displayName,places.websiteUri,places.nationalPhoneNumber",
    "Content-Type": "application/json",
}

enriched_site = 0
enriched_phone = 0
not_found = 0
errors = 0

for idx in to_enrich:
    r = all_rows[idx]
    name = r["nome"].strip()
    city = r["citta"].strip()

    body = {
        "textQuery": f"{name} {city}",
        "languageCode": "it",
        "maxResultCount": 1,
    }

    try:
        resp = httpx.post(
            "https://places.googleapis.com/v1/places:searchText",
            json=body, headers=HEADERS, timeout=10,
        )
        if resp.status_code != 200:
            errors += 1
            time.sleep(0.2)
            continue

        data = resp.json()
        places = data.get("places", [])
        if not places:
            not_found += 1
            time.sleep(0.2)
            continue

        p = places[0]
        site = p.get("websiteUri", "")
        phone = p.get("nationalPhoneNumber", "")

        if site:
            r["sito"] = site
            enriched_site += 1
        if phone and not r["telefono"].strip():
            r["telefono"] = phone
            enriched_phone += 1

    except Exception:
        errors += 1

    # Progress
    if (enriched_site + not_found) % 100 == 0:
        print(f"  [{enriched_site + not_found}] sites:{enriched_site} not_found:{not_found} err:{errors}", flush=True)
        # Incremental save
        with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note"])
            w.writeheader()
            w.writerows(all_rows)

    time.sleep(0.25)  # Rate limit

# Final save
with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note"])
    w.writeheader()
    w.writerows(all_rows)

print(f"\nDONE: enriched {enriched_site} sites, {enriched_phone} phones", flush=True)
print(f"Not found: {not_found} | Errors: {errors}", flush=True)

# Final stats
total = len(all_rows)
ph = sum(1 for r in all_rows if r["telefono"].strip())
wb = sum(1 for r in all_rows if r.get("sito", "").strip())
print(f"Final: {total} total | Phone: {ph} ({100*ph//total}%) | Web: {wb} ({100*wb//total}%)")
