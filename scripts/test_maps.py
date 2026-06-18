"""Test Google Maps Places API (New)."""
import httpx, os, json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

headers = {
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.internationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount,places.types,places.googleMapsUri",
    "Content-Type": "application/json",
}

body = {
    "textQuery": "ristoranti Varese",
    "languageCode": "it",
    "maxResultCount": 5,
}

resp = httpx.post(
    "https://places.googleapis.com/v1/places:searchText",
    json=body,
    headers=headers,
    timeout=15,
)

print(f"Status: {resp.status_code}")
data = resp.json()

if resp.status_code != 200:
    print(f"Error: {json.dumps(data, indent=2, ensure_ascii=False)}")
else:
    places = data.get("places", [])
    print(f"Results: {len(places)}")
    for p in places:
        name = p.get("displayName", {}).get("text", "?")
        addr = p.get("formattedAddress", "")
        phone = p.get("nationalPhoneNumber", "") or p.get("internationalPhoneNumber", "")
        web = p.get("websiteUri", "")
        rating = p.get("rating", "")
        count = p.get("userRatingCount", "")
        types = p.get("types", [])
        print(f"\n  {name}")
        print(f"  Address: {addr}")
        print(f"  Phone: {phone}")
        print(f"  Website: {web}")
        print(f"  Rating: {rating} ({count} reviews)")
        print(f"  Types: {types[:5]}")
