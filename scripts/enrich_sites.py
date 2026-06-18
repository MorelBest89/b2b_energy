"""FASE 4 BATCH: httpx async full-site text extraction for all contacts with website."""
import csv, asyncio, httpx, random, os, sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = r"C:\Users\marco\Projects\consulenza_energy"
CSV_PATH = os.path.join(BASE, "data", "contatti_b2b.csv")

with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    all_rows = list(csv.DictReader(f))

# Only enrich contacts WITH website AND without description
to_enrich = [(i, r) for i, r in enumerate(all_rows) if r.get("sito", "").strip().startswith("http") and not r.get("descrizione", "").strip()]
print(f"Contacts to enrich: {len(to_enrich)} / {len(all_rows)} total")

async def fetch_site(client, sem, i, r):
    url = r["sito"].strip()
    name = r["nome"].strip()[:40]
    
    async with sem:
        try:
            resp = await client.get(url, timeout=8, follow_redirects=True)
            if resp.status_code != 200:
                return i, f"[HTTP {resp.status_code}]"
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Remove noise elements
            for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "iframe"]):
                tag.decompose()
            
            text = soup.get_text(separator=" ", strip=True)
            # Collapse whitespace
            text = " ".join(text.split())
            
            # Build profile: title + meta desc + first 2000 chars of body
            title = soup.title.string.strip() if soup.title else ""
            
            meta_desc = ""
            for meta in soup.find_all("meta"):
                n = (meta.get("name") or "").lower()
                p = (meta.get("property") or "").lower()
                if n in ("description",) or p in ("og:description",):
                    meta_desc = meta.get("content", "")
                    break
            
            parts = []
            if title:
                parts.append(f"[{title}]")
            if meta_desc:
                parts.append(meta_desc)
            
            body = text.strip()
            if body:
                parts.append(body[:2000])
            
            return i, " | ".join(parts)[:3000]
            
        except httpx.TimeoutException:
            return i, "[TIMEOUT]"
        except Exception as e:
            return i, f"[ERR: {type(e).__name__}]"


async def main():
    sem = asyncio.Semaphore(30)  # 30 concurrent connections
    
    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        limits=httpx.Limits(max_connections=30),
        timeout=10,
    ) as client:
        tasks = [fetch_site(client, sem, i, r) for i, r in to_enrich]
        
        done = 0
        success = 0
        errors = 0
        
        for coro in asyncio.as_completed(tasks):
            i, result = await coro
            all_rows[i]["descrizione"] = result
            
            if result.startswith("["):
                errors += 1
            else:
                success += 1
            done += 1
            
            if done % 100 == 0:
                print(f"  [{done}/{len(to_enrich)}] ok:{success} err:{errors}", flush=True)
                # Incremental save
                with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
                    w = csv.DictWriter(f, fieldnames=["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note"])
                    w.writeheader()
                    w.writerows(all_rows)
    
    print(f"  [{done}/{len(to_enrich)}] ok:{success} err:{errors} DONE", flush=True)

asyncio.run(main())

# Final save
with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["fonte","categoria","citta","nome","indirizzo","telefono","sito","descrizione","note"])
    w.writeheader()
    w.writerows(all_rows)

print(f"\nPhase 4 complete: {sum(1 for r in all_rows if r['descrizione'].strip() and not r['descrizione'].startswith('['))} descriptions enriched")
