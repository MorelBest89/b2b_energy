#!/usr/bin/env python3
"""
Converti HTML report -> PDF con Playwright.
- Immagini embedded come base64 (PDF standalone, inviabile ai clienti)
- Link preservati
- Header riformattato, nessun taglio tra sezioni, max 2 pagine A4

Uso:
  python genera_report.py "C:/Users/marco/Downloads/Cliente - Report.html"
  python genera_report.py report.html output.pdf
"""

import base64
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# Cartelle aggiuntive dove cercare le immagini (oltre alla cartella dell'HTML)
FALLBACK_IMAGE_DIRS = [Path(__file__).parent]

PRINT_OVERRIDES = """
<style>
@media print {
  /* overflow:hidden taglia il contenuto ai bordi di pagina */
  .report  { overflow: visible !important; box-shadow: none !important;
             border-radius: 0 !important; max-width: 100% !important; }
  body     { background: #fff !important; padding: 0 !important; }

  /* Header */
  .header  { padding: 14px 28px 16px !important; }
  .header h1   { font-size: 1.2rem !important; margin-bottom: 3px !important; }
  .header .sub { font-size: .8rem  !important; }
  .header .meta { font-size: .76rem !important; gap: 14px !important; }

  /* Body */
  .body    { padding: 14px 24px 20px !important; }

  /* Ogni sezione resta intera su una pagina */
  .section       { margin-bottom: 10px !important;
                   break-inside: avoid !important; page-break-inside: avoid !important; }
  .section-title { margin-bottom: 6px  !important; font-size: .7rem !important;
                   break-after: avoid  !important; page-break-after:  avoid !important; }

  .card    { padding: 10px 12px !important; margin-bottom: 6px !important;
             break-inside: avoid !important; page-break-inside: avoid !important; }
  .card h3 { font-size: .85rem !important; margin-bottom: 4px !important; }
  .card p  { font-size: .75rem !important; margin-bottom: 4px !important; }

  .row     { font-size: .78rem !important; padding: 2px 0 !important; }

  .table   { font-size: .75rem !important;
             break-inside: avoid !important; page-break-inside: avoid !important; }
  .table th, .table td { padding: 4px 8px !important; }

  .cta-box      { padding: 14px 18px !important;
                  break-inside: avoid !important; page-break-inside: avoid !important; }
  .cta-box h3   { font-size: .95rem !important; margin-bottom: 4px !important; }
  .cta-box p    { font-size: .78rem !important; margin-bottom: 10px !important; }
  .cta-box .phone { font-size: 1.1rem !important; }

  .footer  { padding: 8px 24px !important; font-size: .7rem !important; }
}
</style>
"""


# ─── Header rewrite ───────────────────────────────────────────────────────────

def _find_closing_div(html: str, open_pos: int) -> int:
    """Trova la posizione dopo il </div> che chiude il div aperto a open_pos."""
    depth = 0
    i = open_pos
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            i = html.index('>', i) + 1
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                return i + 6
            i += 6
        else:
            i += 1
    return len(html)


def fix_header(html: str) -> str:
    """
    Riscrive il div.header con un layout più curato per la stampa:
      [Titolo + subtitle + link recensione]  |  [Logo]
      ─────────────────────────────────────────────────
      [📋 Cliente]  [📍 Città]  [📅 Data]
    """
    start = html.find('<div class="header">')
    if start == -1:
        return html
    end = _find_closing_div(html, start)
    h = html[start:end]

    def rx(pattern, default=''):
        m = re.search(pattern, h, re.DOTALL)
        return m.group(1) if m else default

    title = rx(r'<h1>(.*?)</h1>', 'Report di Efficienza Energetica')
    sub   = rx(r'<div class="sub">(.*?)</div>')
    meta  = rx(r'<div class="meta">(.*?)</div>')

    # Logo: ridimensiona a 72px; aggiunge margine sinistro
    img_m = re.search(r'<img\s[^>]+>', h)
    img   = img_m.group(0) if img_m else ''
    img   = re.sub(r'height:\s*\d+px', 'height:72px', img)
    if 'margin-left' not in img:
        img = img.replace('style="', 'style="margin-left:20px;flex-shrink:0;', 1)

    # Link recensione: mantieni href, standardizza stile
    review_m = re.search(r'<a\s[^>]*recensioni[^>]*>.*?</a>', h, re.DOTALL)
    review   = review_m.group(0) if review_m else ''
    review   = re.sub(r'font-size:[^;]*;', 'font-size:.8rem;', review)

    # URL testo sotto il link (opzionale)
    url_m = re.search(r'(mm-energy-lab[^\s<"]+)', h)
    url   = (f'<div style="font-size:.62rem;opacity:.5;margin-top:3px;">'
             f'{url_m.group(1)}</div>') if url_m else ''

    new_header = (
        '<div class="header">\n'
        '  <div style="display:flex;justify-content:space-between;'
        'align-items:flex-start;margin-bottom:12px;">\n'
        '    <div style="flex:1;min-width:0;">\n'
        f'      <h1>{title}</h1>\n'
        f'      <div class="sub" style="margin-bottom:10px;">{sub}</div>\n'
        f'      {review}\n'
        f'      {url}\n'
        '    </div>\n'
        f'    {img}\n'
        '  </div>\n'
        '  <div class="meta" style="border-top:1px solid rgba(255,255,255,.25);'
        'padding-top:10px;">\n'
        f'    {meta}\n'
        '  </div>\n'
        '</div>'
    )

    return html[:start] + new_header + html[end:]


# ─── Image embedding ──────────────────────────────────────────────────────────

def embed_images(html: str, html_dir: Path) -> str:
    """Sostituisce tutti i src delle <img> con data URI base64."""
    def replace(m):
        src = m.group(1)
        if src.startswith('data:'):
            return m.group(0)
        candidates = [html_dir / src] + [d / Path(src).name for d in FALLBACK_IMAGE_DIRS]
        for path in candidates:
            try:
                p = path.resolve()
                if p.exists():
                    mime = 'image/png' if p.suffix.lower() == '.png' else 'image/jpeg'
                    data = base64.b64encode(p.read_bytes()).decode()
                    return f'src="data:{mime};base64,{data}"'
            except Exception:
                continue
        return m.group(0)

    return re.sub(r'src="([^"]+)"', replace, html)


# ─── Main ─────────────────────────────────────────────────────────────────────

def html_to_pdf(html_path: str, pdf_path: str) -> None:
    src = Path(html_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f'File non trovato: {src}')

    html = src.read_text(encoding='utf-8')
    html = fix_header(html)
    html = embed_images(html, src.parent)
    html = html.replace('</head>', PRINT_OVERRIDES + '</head>')

    tmp = src.parent / f'_tmp_{src.stem}.html'
    try:
        tmp.write_text(html, encoding='utf-8')
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f'file:///{tmp.as_posix()}')
            page.wait_for_load_state('networkidle')
            page.pdf(
                path=str(Path(pdf_path).resolve()),
                format='A4',
                print_background=True,
                margin={'top': '10mm', 'bottom': '10mm',
                        'left': '12mm', 'right': '12mm'},
            )
            browser.close()
    finally:
        if tmp.exists():
            tmp.unlink()

    size_kb = Path(pdf_path).stat().st_size // 1024
    print(f'PDF generato: {pdf_path} ({size_kb} KB)')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: python genera_report.py <report.html> [output.pdf]')
        sys.exit(1)
    html_in = sys.argv[1]
    pdf_out = (sys.argv[2] if len(sys.argv) > 2
               else str(Path(html_in).with_suffix('.pdf')))
    html_to_pdf(html_in, pdf_out)
