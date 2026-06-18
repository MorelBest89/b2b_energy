"""FASE 4 TEST: httpx async full-site text extraction on 20 websites."""
import csv, random, asyncio, httpx, re
from bs4 import BeautifulSoup

CSV_PATH = r"C:\Users\marco\Projects\consulenza_energy\data\contatti_b2b.csv"

with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    all_rows = list(csv.DictReader(f))

# Pick 20 contacts WITH website
with_site = [r for r in all_rows if r.get("sito", "").strip().startswith("http")]
sample = random.sample(with_site, min(20, len(with_site)))

print(f"Testing full-site extraction on {len(sample)} sites\n")

async def fetch_site(client, url):
    """Fetch full text content from a website."""
    try:
        resp = await client.get(url, timeout=10, follow_redirects=True)
        if resp.status_code != 200:
            return f"[HTTP {resp.status_code}]"
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Remove script, style, nav, header, footer
        for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
            tag.decompose()
        
        text = soup.get_text(separator="\n", strip=True)
        # Clean: collapse whitespace, remove very short lines
        lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 30]
        text = "\n".join(lines)
        
        # Find key sections
        title = soup.title.string.strip() if soup.title else ""
        meta_desc = ""
        for meta in soup.find_all("meta"):
            if meta.get("name", "").lower() in ("description", "og:description"):
                meta_desc = meta.get("content", "")
                break
        
        result = f"TITLE: {title}\n"
        if meta_desc:
            result += f"DESC: {meta_desc}\n"
        result += f"SIZE: {len(text)} chars, {len(lines)} lines\n"
        result += f"TEXT (first 500):\n{text[:500]}..."
        return result
        
    except Exception as e:
        return f"[ERR: {type(e).__name__}]"


async def main():
    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        limits=httpx.Limits(max_connections=20),
    ) as client:
        tasks = []
        for r in sample:
            url = r["sito"].strip()
            tasks.append(fetch_site(client, url))
        
        results = await asyncio.gather(*tasks)
        
        success = 0
        for i, (r, result) in enumerate(zip(sample, results)):
            print(f"[{i+1}] {r['nome'][:40]} | {r['citta']}")
            print(f"    URL: {r['sito'][:80]}")
            print(f"    {result[:300]}")
            if not result.startswith("["):
                success += 1
            print()
    
    print(f"Success: {success}/{len(sample)}")

asyncio.run(main())
