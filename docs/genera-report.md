# Come generare un report PDF

## Prerequisiti

### 1. Python 3.10 o superiore
Scarica da [python.org](https://www.python.org/downloads/).
Durante l'installazione su Windows, spunta **"Add Python to PATH"**.

Verifica con:
```
python --version
```

### 2. Librerie Python
```
pip install playwright
```

### 3. Browser Chromium (scaricato da Playwright, ~130 MB)
```
playwright install chromium
```

Questi tre comandi vanno eseguiti **una sola volta** su ogni PC nuovo.

---

## Generare il PDF

```
python genera_report.py "percorso\al\Cliente - Report.html"
```

Output: stesso nome del file HTML, estensione `.pdf`, stessa cartella.

Per scegliere dove salvare il PDF:
```
python genera_report.py "Cliente - Report.html" "output\Cliente - Report.pdf"
```

---

## Struttura del file HTML

Il report è un file HTML con questa struttura fissa. Non cambiare le classi CSS.

```html
<div class="report">

  <div class="header">
    <!-- Titolo, logo, link recensione, info cliente -->
    <!-- Logo: usa un path relativo a logo.jpg -->
    <img src="../../../logo.jpg" ...>
  </div>

  <div class="body">

    <div class="section">
      <div class="section-title">1. Nome Sezione</div>
      <div class="card">
        <div class="row">
          <span class="label">Etichetta</span>
          <span class="value">Valore</span>
        </div>
      </div>
    </div>

    <!-- ... altre sezioni ... -->

  </div>
</div>
```

Classi disponibili:
- `.card` — scheda grigio chiaro con bordo
- `.row` + `.label` / `.value` / `.save` — riga a due colonne (label / valore verde)
- `.table` — tabella standard con header grigio
- `.badge.badge-red` / `.badge-green` / `.badge-yellow` — badge colorato
- `.cta-box` — box verde finale con numero di telefono

---

## Il logo

Lo script cerca il logo in questo ordine:
1. Path relativo all'HTML (es. `../../../logo.jpg`)
2. Cartella dello script `genera_report.py` (es. `logo.jpg` in `consulenza_energy/`)

Se il logo non appare nel PDF, metti una copia di `logo.jpg` nella stessa cartella dell'HTML.

---

## Template per un nuovo cliente

Copia `Timpani Tonino Secondo - Report.html` dalla cartella Downloads, rinominalo con il nome del nuovo cliente e modifica:

| Cosa cambiare | Dove nel file |
|---|---|
| Nome cliente | `class="header"` → `class="meta"` → prima `<span>` |
| Città | Seconda `<span>` nel meta |
| Data | Terza `<span>` nel meta |
| Fornitore, spesa, consumi | Sezione 1, div con class `row` |
| Interventi | Sezione 2, `.card` con descrizione e righe |
| Confronto mercato | Sezione 3, righe della `table` |
| Energia reattiva | Sezione 4 |
| Riepilogo interventi | Sezione 5, righe `table` |
| Proposta e telefono | Sezione 6, `.cta-box` |

---

## Troubleshooting

**"playwright: command not found"**
→ Usa `python -m playwright install chromium`

**Logo non appare**
→ Copia `logo.jpg` nella stessa cartella dell'HTML

**Errore `ModuleNotFoundError: No module named 'playwright'`**
→ Esegui `pip install playwright` e poi `playwright install chromium`

**PDF ha più di 2 pagine**
→ Riduci il testo nei campi più lunghi, oppure rimuovi la sezione "Energia Reattiva" se non rilevante per quel cliente
