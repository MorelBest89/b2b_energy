"""FASE 4 v2: FULL text extraction + structured profile + scoring."""
import csv, asyncio, httpx, os, sys, re
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = r"C:\Users\marco\Projects\consulenza_energy"
CSV_PATH = os.path.join(BASE, "data", "contatti_b2b.csv")

with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    all_rows = list(csv.DictReader(f))

to_enrich = [(i, r) for i, r in enumerate(all_rows) if r.get("sito", "").strip().startswith("http")]
print(f"Fetching FULL text for {len(to_enrich)} sites")

async def fetch_full(client, sem, i, r):
    url = r["sito"].strip()
    async with sem:
        try:
            resp = await client.get(url, timeout=8, follow_redirects=True)
            if resp.status_code != 200:
                return i, None
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "iframe"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
            text = " ".join(text.split())
            
            title = soup.title.string.strip() if soup.title else ""
            meta_desc = ""
            for meta in soup.find_all("meta"):
                if (meta.get("name") or "").lower() == "description" or (meta.get("property") or "").lower() == "og:description":
                    meta_desc = meta.get("content", "")
                    break
            
            return i, {"title": title, "meta": meta_desc, "text": text}
        except:
            return i, None

async def main():
    sem = asyncio.Semaphore(25)
    site_data = {}
    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        limits=httpx.Limits(max_connections=25), timeout=10,
    ) as client:
        tasks = [fetch_full(client, sem, i, r) for i, r in to_enrich]
        done = 0
        for coro in asyncio.as_completed(tasks):
            i, data = await coro
            site_data[i] = data
            done += 1
            if done % 250 == 0:
                ok = sum(1 for v in site_data.values() if v is not None)
                print(f"  [{done}/{len(to_enrich)}] ok:{ok}", flush=True)
    
    # Write full text to JSON for processing
    ok = sum(1 for v in site_data.values() if v is not None)
    print(f"  [{done}/{len(to_enrich)}] DONE ok:{ok} ({100*ok//len(to_enrich)}%)", flush=True)
    
    # Save intermediate data
    import json
    json_path = os.path.join(BASE, "data", "site_texts.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in site_data.items() if v}, f, ensure_ascii=False)
    print(f"Saved {ok} site texts to {json_path}")

asyncio.run(main())
