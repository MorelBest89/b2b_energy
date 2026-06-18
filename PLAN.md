# PLAN.md — Execution Roadmap M&M Energy

> **Obiettivo:** Portare Morel da 0 a 3+ check B2B paganti in 90 giorni.
> **Documento master:** [business-check-energetico-completo.md](docs/business-check-energetico-completo.md)

---

## FASE 0 — Raccolta Contatti B2B

> **Stato:** 371 contatti raccolti con 327 telefoni (88% copertura). Pronto per CRM.
> **Script:** `scrape_contatti.py` (PagineGialle via Playwright headed)

### 0.1 Fonti disponibili — ordinate per potenziale

| # | Fonte | Contatti stimati | Telefoni | Siti | Costo | Difficolta | Stato |
|---|-------|:---:|:---:|:---:|---|---|---|
| 1 | **PagineGialle — search results + pagination** | 2,000-5,000 | 85% | 30% (detail pages) | Gratis | Media | **IN CORSO** — 371 ottenuti, da estendere con paginazione e piu citta |
| 2 | **OpenStreetMap Overpass API** | 500-1,500 | 25% | 30% | Gratis | Bassa | **FATTO** — 309 contatti (low phone coverage) |
| 3 | **Google Maps — SerpAPI o BrightData** | 1,000-3,000 | 90% | 70% | €50-100 API key | Bassa | Da valutare |
| 4 | **Camera di Commercio / Registro Imprese** | 5,000+ aziende | 0% (no tel) | 40% | Gratis (visura) | Alta | Da valutare — no telefoni |
| 5 | **Acquistare liste B2B (Cerved, Kompass)** | 500-2,000 | 90% | 80% | €100-500 | Molto Bassa | Opzione fast — pre-filtrate e verificate |
| 6 | **TheFork scraping** (solo ristoranti) | 200-500 | 50% | 80% | Gratis | Media | Solo ristoranti, non prioritario |
| 7 | **LinkedIn Sales Navigator** | 200-500 aziende | 0% | 70% | €80/mese | Bassa | Nomi azienda + decision maker, zero telefoni |
| 8 | **PagineBianche** (elenco telefonico) | 10,000+ | 100% | 0% | Gratis | Media | Solo telefoni + indirizzi, no categoria |

### 0.2 Raccomandazione

1. **Completare PagineGialle** con paginazione + piu citta (Saronno, Cantu, Luino, Tradate, Erba, Mariano, Olgiate, Verbania, Stresa) → target **800-1,500 contatti**
2. **Fondere** i 309 contatti OSM gia raccolti con i 371 PagineGialle → deduplica
3. **Opzionale:** acquistare lista verificata da Cerved/Kompass per categorie mancanti (€200-300)

### 0.3 CSV Output

- [x] `contatti_b2b.csv` generato (371 contatti, 327 con telefono)
- [ ] Colonne: Nome, Indirizzo, Categoria, Citta, Telefono, Sito, Descrizione, Note
- [ ] Importare in Google Sheets condiviso con Morel
- [ ] Aggiungere colonne CRM: Stato (Da Contattare → Contattato → Appuntamento → Check → Cliente), Data Contatto, Note Chiamata

### 0.4 Categorie target coperte

| Categoria | Contatti | Con telefono |
|-----------|:---:|:---:|
| Ristoranti/Pizzerie | 141 | 110 |
| Hotel/B&B | 74 | 72 |
| Palestre/Centri Sportivi | 72 | 72 |
| Officine/Artigiani | 53 | 53 |
| Lavanderie Industriali | 31 | 31 |

### 0.5 Tracking Table — RACCOLTA CONTATTI

| Legenda | |
|---|---|
| ✅ **Fatto** | Scraping completato, dati in CSV |
| 🔄 **In corso** | Avviato ma incompleto |
| ⬜ **Da fare** | Non ancora iniziato |
| **-** | Restituito 0 in quel run (da ritentare) |
| **Nr** | Contatti raccolti |

| Canale | Cat. | Varese | Gallarate | Busto A. | Saronno | Tradate | Malnate | Luino | Gavirate | Somma L. | Cassano M. | Como | Cantu | Erba | Mariano C. | Olgiate C. | Lomazzo | Fino M. | Verbania | Stresa | Arona |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **PagineGialle** | Rist. | ✅172 | - | ✅167 | - | - | - | - | - | ✅167 | ✅146 | - | ✅169 | - | ✅159 | ✅159 | - | - | - | ✅170 | ✅171 | **1.313** |
| | Palestre | ✅149 | ✅105 | - | - | - | - | ✅28 | - | ✅47 | ✅31 | - | - | ✅123 | - | - | ✅71 | - | - | ✅17 | - | **571** |
| | Officine | ✅150 | - | - | - | - | ✅43 | - | - | ✅114 | - | ✅126 | - | ✅114 | ✅106 | - | ✅102 | - | - | - | ✅83 | **838** |
| | Lavand. | ✅13 | - | - | ✅64 | - | - | ✅5 | - | - | - | - | - | ✅15 | ✅13 | ✅9 | - | ✅5 | - | ✅2 | - | **126** |
| | Hotel | ✅172 | - | - | ✅165 | - | - | ✅155 | - | ✅136 | - | ✅142 | - | - | - | - | ✅61 | - | ✅140 | ✅96 | **1.096** |
| **OpenStreetMap** | Tutte | 309 totali (25% telefono, archiviati separatamente) |
| **Google Maps** | Tutte | ✅ 1.461 contatti, 95% tel, 76% web (dettaglio in data/contatti_googlemaps.csv) |
| **Liste B2B** | Tutte | ⬜ |
| **TheFork** | Rist. | ⬜ |

### 0.5.1 — RIEPILOGO FINALE

| Fonte | Contatti | Tel | Web | Stato |
|---|---|---|---|---|
| PagineGialle (screened) | 2.082 | 1.993 (95%) | 0 (0%) | ✅ |
| Google Maps API | 1.461 | 1.393 (95%) | 1.119 (76%) | ✅ |
| **TOTALE MERGED** | **3.543** | **3.386 (95%)** | **1.123 (31%)** | ✅ |

### 0.6 Esecuzione

```bash
python scrape_contatti.py
```

---

## FASE 1 — Setup Tecnico (Giorni 1-5)

**Documento:** [roadmap-30-giorni.md](docs/roadmap-30-giorni.md)

### 1.1 Acquisti (Giorno 1) — Budget €350-500

- [ ] **Termocamera smartphone:** InfiRay P2 Pro o FLIR One Pro (Amazon)
- [ ] **Igrometro digitale** (Amazon/Leroy Merlin, €15-30)
- [ ] **Metro laser** (Amazon, €30-50)
- [ ] **Anemometro economico** o accendino a fiamma lunga per test spifferi
- [ ] **Biglietti da visita:** 500 pz su Vistaprint. Testo: *"Morel — Ingegnere Energetico — Check Energetico + Bonus Edilizi"*

### 1.2 Brand (Giorno 2)

- [ ] **Logo:** Vedere concept da Gemini (logo brief archiviato) se non ancora creato
- [ ] **Google Business Profile:** nome "Morel — Consulenza Energetica Varese", categorie Ingegnere + Consulente Energetico
- [ ] **Brochure one-pager:** Usare [brochure-morel.md](docs/brochure-morel.md) come base per PDF professionale

### 1.3 Template operativi (Giorno 3-5)

- [ ] **Template Report (Word/PDF):** struttura standard con foto termiche, priorita, costi, risparmi, bonus
- [ ] **Checklist Sopralluogo:** da [check-sopralluogo.md](docs/check-sopralluogo.md)
- [ ] **Contratto B2B:** con clausola "3x Risparmio o Rimborsato" (da [brochure-morel.md](docs/brochure-morel.md))
- [ ] **Script telefonico:** da [script-vendita.md](docs/script-vendita.md)

---

## FASE 2 — Attivazione Rete (Giorni 6-15)

**Documenti:** [piano-3-contatti.md](docs/piano-3-contatti.md), [sinergie-flipping.md](docs/sinergie-flipping.md)

### 2.1 I 3 Contatti Caldi

- [ ] **Amico 1 — Amministratore Condomini:** offrire 1 check gratuito parti comuni
- [ ] **Amico 2 — Facciatista:** accordo referral reciproco (facciata → cappotto = upselling incrociato)
- [ ] **Amico 3 — Installatore FV:** referral reciproco (check prima del FV)

### 2.2 Sinergia Marco

- [ ] Definire % referral sui flip di Marco
- [ ] Primo sopralluogo su immobile di Marco (test del processo end-to-end)

### 2.3 Prospezione attiva dal CRM

- [ ] **Ogni giorno:** chiamare 5-10 contatti dal CRM (Fase 0)
- [ ] **Ogni giorno:** visitare di persona 2-3 attivita in orario di calma
- [ ] **Script B2B (da [script-vendita.md](docs/script-vendita.md)):** presentazione in 2 minuti, focus su ROI, chiedere la bolletta

---

## FASE 3 — Primi Check e Validazione (Giorni 16-30)

**Documenti:** [check-sopralluogo.md](docs/check-sopralluogo.md), [dal-check-alla-soluzione.md](docs/dal-check-alla-soluzione.md), [gemini-come-leggere-bollette.md](docs/gemini-come-leggere-bollette.md)

### 3.1 Obiettivo: 3+ check paganti

- [ ] Eseguire check su immobile Marco (test gratuito)
- [ ] Check gratuito su condominio Amico 1
- [ ] **Target:** 3 check B2B a pagamento (€490 cad) entro giorno 30

### 3.2 Per ogni check

- [ ] Sopralluogo con le 7 fasi (checklist da [check-sopralluogo.md](docs/check-sopralluogo.md))
- [ ] Analisi bollette (guida da [gemini-come-leggere-bollette.md](docs/gemini-come-leggere-bollette.md))
- [ ] Report consegnato entro 48h
- [ ] Presentazione upsell: bonus ENEA (+€300), coordinamento lavori (+€1.500, 10% sui lavori)

### 3.3 Raccolta feedback

- [ ] Chiedere recensione Google a ogni cliente
- [ ] Chiedere 1 referral a ogni cliente
- [ ] Aggiornare CRM con esito chiamata/check

---

## FASE 4 — Consolidamento (Mesi 2-3)

**Documento:** [business-check-energetico-completo.md](docs/business-check-energetico-completo.md) §13

### 4.1 Standardizzazione

- [ ] Template report definitivo
- [ ] Processo CRM rodato (contatto → chiamata → appuntamento → check → report → upsell)
- [ ] 5 partner artigiani fissi (elettricista, idraulico, infissista, imbianchino, caldaista)

### 4.2 Canali di acquisizione scalabili

- [ ] **ProntoPro:** account "Check Energetico" (budget €100/mese)
- [ ] **Facebook Ads:** target Varese/Como 35-65 anni, interesse "casa"
- [ ] **Google Business Profile:** raggiungere 10+ recensioni a 5 stelle

### 4.3 Partnership strutturate

- [ ] 5+ amministratori condominiali come referral fissi
- [ ] 3+ agenzie immobiliari
- [ ] 2+ associazioni di categoria (Confcommercio, Confesercenti) come canale seminari

---

## FASE 5 — Scalata (Mesi 4-12)

- [ ] **Reddito target:** 4-6 check/mese + 2-3 bonus/mese = €2.000-3.000/mese
- [ ] **Rete artigiani:** 5 partner fissi con accordo di referral
- [ ] **Lead generation passiva:** 30% clienti da passaparola
- [ ] **Primo junior:** formare un tecnico per sopralluoghi semplici
- [ ] **B2B ricorrente:** contratto manutenzione annuale €200/mese per cliente

---

## Kill Trigger

| Deadline | Criterio | Azione se fallito |
|----------|----------|-------------------|
| 30 giorni | 0 clienti paganti | Cambiare prezzo o canale |
| 90 giorni | <3 check paganti | Rivedere modello: B2C invece di B2B? Prezzo? Territorio? |
