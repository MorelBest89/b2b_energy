"""
Scrape B2B contacts using OpenStreetMap Overpass API.
Free, no anti-bot, structured JSON response.
"""
import httpx, csv, time, os, re

BASE = r"C:\Users\marco\Projects\consulenza_energy"
OUTPUT = os.path.join(BASE, "contatti_b2b.csv")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Amenity/keyword mapping for OSM + city boundary search
# Using admin_level=8 (comune) for city boundaries
QUERIES = [
    # (categoria, osm_tag, cities)
    ("Ristoranti/Pizzerie", 'node["amenity"~"restaurant|cafe|fast_food|pub|bar"]', ["Varese", "Como", "Gallarate", "Busto Arsizio"]),
    ("Palestre", 'node["leisure"~"fitness_centre|sports_centre|gym"]', ["Varese", "Como", "Gallarate", "Busto Arsizio"]),
    ("Officine/Artigiani", 'node["shop"~"car_repair|motorcycle_repair|tyres"]', ["Varese", "Como"]),
    ("Falegnamerie", 'node["craft"~"carpenter|joiner"]', ["Varese", "Como"]),
    ("Lavanderie", 'node["shop"~"laundry|dry_cleaning"]', ["Varese", "Como", "Gallarate", "Busto Arsizio"]),
    ("Hotel", 'node["tourism"~"hotel|guest_house|motel"]', ["Como", "Varese"]),
]

def build_query(osm_tag, city):
    return f"""
[out:json][timeout:25];
area["name"="{city}"]["admin_level"="8"]->.a;
{osm_tag}(area.a);
out body 100;
"""

def search_city(categoria, osm_tag, city):
    query = build_query(osm_tag, city)
    print(f"[{categoria}] {city} ...", end=" ", flush=True)
    try:
        resp = httpx.post(OVERPASS_URL, data=query, timeout=30, headers={"User-Agent": "M&MEnergy/1.0"})
        data = resp.json()
        elements = data.get("elements", [])
        results = []
        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name", "")
            if not name:
                continue
            street = tags.get("addr:street", "")
            housenumber = tags.get("addr:housenumber", "")
            city_tag = tags.get("addr:city", city)
            address = f"{street} {housenumber}, {city_tag}".strip(", ")
            phone = tags.get("phone", "") or tags.get("contact:phone", "")
            website = tags.get("website", "") or tags.get("contact:website", "")
            email = tags.get("email", "") or tags.get("contact:email", "")
            description = tags.get("description", "")
            
            results.append({
                "categoria": categoria,
                "citta": city,
                "nome": name,
                "indirizzo": address,
                "telefono": phone,
                "email": email,
                "sito": website,
                "descrizione": description,
                "note": "",
            })
        print(f"{len(results)} results", flush=True)
        return results
    except Exception as e:
        print(f"ERR: {e}", flush=True)
        return []

# ── MAIN ──
all_results = []
seen = set()

for categoria, osm_tag, cities in QUERIES:
    for city in cities:
        results = search_city(categoria, osm_tag, city)
        for r in results:
            key = (r["nome"].lower(), r["citta"].lower())
            if key not in seen:
                seen.add(key)
                all_results.append(r)
        time.sleep(1.5)  # Respect rate limit

# Write CSV
with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["categoria", "citta", "nome", "indirizzo", "telefono", "email", "sito", "descrizione", "note"])
    w.writeheader()
    for r in all_results:
        w.writerow(r)

print(f"\nTOTALE: {len(all_results)} contatti in {OUTPUT}")
# Breakdown
from collections import Counter
cat_counts = Counter(r["categoria"] for r in all_results)
for cat, count in cat_counts.most_common():
    print(f"  {cat}: {count}")
