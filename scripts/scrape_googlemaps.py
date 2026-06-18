"""Google Maps Places API — Full contact collection via Text Search."""
import csv, time, os, httpx
from dotenv import load_dotenv
from collections import Counter

BASE = r"C:\Users\marco\Projects\consulenza_energy"
load_dotenv(os.path.join(BASE, ".env"))
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

HEADERS = {
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.internationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount,places.types,places.googleMapsUri",
    "Content-Type": "application/json",
}

# One API call can return max 20 results. We need to paginate if >20.
CATEGORIES = [
    ("Ristoranti/Pizzerie", "ristoranti"),
    ("Palestre", "palestre"),
    ("Officine/Artigiani", "officine meccaniche"),
    ("Lavanderie", "lavanderie industriali"),
    ("Hotel/B&B", "hotel"),
]

CITIES = [
    "Varese", "Gallarate", "Busto Arsizio", "Saronno", "Tradate",
    "Malnate", "Luino", "Gavirate", "Somma Lombardo", "Cassano Magnago",
    "Como", "Cantu", "Erba", "Mariano Comense", "Olgiate Comasco",
    "Lomazzo", "Fino Mornasco", "Verbania", "Stresa", "Arona",
    "Laveno Mombello", "Angera",
]

def search(category, query, city):
    results = []
    body = {
        "textQuery": f"{query} {city}",
        "languageCode": "it",
        "maxResultCount": 20,
    }
    try:
        resp = httpx.post(
            "https://places.googleapis.com/v1/places:searchText",
            json=body,
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code != 200:
            return results
        data = resp.json()
        for p in data.get("places", []):
            name = (p.get("displayName") or {}).get("text", "")
            if not name:
                continue
            phone = p.get("nationalPhoneNumber", "") or p.get("internationalPhoneNumber", "") or ""
            results.append({
                "fonte": "GoogleMaps",
                "categoria": category,
                "citta": city,
                "nome": name,
                "indirizzo": p.get("formattedAddress", ""),
                "telefono": phone,
                "sito": p.get("websiteUri", ""),
                "descrizione": "",
                "note": f"Rating: {p.get('rating', '')}/{p.get('userRatingCount', '')}",
            })
    except Exception as e:
        pass
    return results


# ── MAIN ──
all_results = []
seen = set()
total = 0

for cat, query in CATEGORIES:
    print(f"\n{'='*60}")
    print(f"[{cat}] — {len(CITIES)} cities", flush=True)
    for city in CITIES:
        print(f"  {city} ...", end=" ", flush=True)
        cards = search(cat, query, city)
        added = 0
        for c in cards:
            key = (c["nome"].lower(), c["indirizzo"].lower())
            if key not in seen:
                seen.add(key)
                all_results.append(c)
                added += 1
        total += added
        ph = sum(1 for c in cards if c["telefono"])
        wb = sum(1 for c in cards if c["sito"])
        print(f"+{added} (ph:{ph} web:{wb} | tot:{total})", flush=True)
        time.sleep(0.3)  # Rate limit

outpath = os.path.join(BASE, "data", "contatti_googlemaps.csv")
with open(outpath, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note"])
    w.writeheader()
    w.writerows(all_results)

ph_tot = sum(1 for r in all_results if r["telefono"].strip())
wb_tot = sum(1 for r in all_results if r["sito"].strip())
print(f"\nSAVED: {len(all_results)} contacts (ph:{ph_tot} web:{wb_tot}) -> {outpath}")
cat_counts = Counter(r["categoria"] for r in all_results)
for c, n in cat_counts.most_common():
    print(f"  {c}: {n}")
