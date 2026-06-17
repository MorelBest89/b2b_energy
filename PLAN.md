# PLAN.md — Execution Roadmap M&M Energy

> **Obiettivo:** Portare Morel da 0 a 3+ check B2B paganti in 90 giorni.
> **Documento master:** [business-check-energetico-completo.md](business-check-energetico-completo.md)

---

## FASE 0 — Raccolta Contatti B2B (ORA)

**Obiettivo:** Fornire a Morel un CRM già popolato con ~100 contatti profilati, pronto da chiamare.

### 0.1 Setup strumentazione (Marco)

- [x] Script scraping multi-categoria su Varese/Como/Gallarate/Busto
- [ ] Generare CSV pronto per Google Sheets con colonne:
  - Nome Azienda, Indirizzo, Tipologia, Telefono, Email, Sito, Descrizione Business, Note
- [ ] Importare CSV in Google Sheets condiviso con Morel
- [ ] Aggiungere colonne CRM: Stato (Da Contattare/Contattato/Appuntamento/Check Fatto/Cliente), Data Contatto, Note Chiamata

### 0.2 Categorie target

| # | Categoria | Keyword PagineGialle | Citta |
|---|-----------|---------------------|-------|
| 1 | Ristoranti/Pizzerie | ristoranti, pizzerie | Varese, Como, Gallarate, Busto Arsizio |
| 2 | Palestre/Centri Sportivi | palestre, centri sportivi | Varese, Como, Gallarate, Busto Arsizio |
| 3 | Officine/Artigiani | officine meccaniche, falegnamerie | Varese, Como, Gallarate, Busto Arsizio |
| 4 | Lavanderie Industriali | lavanderie industriali, tintorie | Varese, Como, Gallarate, Busto Arsizio |
| 5 | Hotel/B&B | hotel, bed and breakfast | Como, Varese, Lago Maggiore |

### 0.3 Esecuzione

```bash
python scrape_contatti.py
```

**Output:** `contatti_b2b.csv` con ~100 contatti profilati.

---

## FASE 1 — Setup Tecnico (Giorni 1-5)

**Documento:** [roadmap-30-giorni.md](roadmap-30-giorni.md)

### 1.1 Acquisti (Giorno 1) — Budget €350-500

- [ ] **Termocamera smartphone:** InfiRay P2 Pro o FLIR One Pro (Amazon)
- [ ] **Igrometro digitale** (Amazon/Leroy Merlin, €15-30)
- [ ] **Metro laser** (Amazon, €30-50)
- [ ] **Anemometro economico** o accendino a fiamma lunga per test spifferi
- [ ] **Biglietti da visita:** 500 pz su Vistaprint. Testo: *"Morel — Ingegnere Energetico — Check Energetico + Bonus Edilizi"*

### 1.2 Brand (Giorno 2)

- [ ] **Logo:** Vedere [concept da Gemini](gemini-concept-logo.md) se non ancora creato
- [ ] **Google Business Profile:** nome "Morel — Consulenza Energetica Varese", categorie Ingegnere + Consulente Energetico
- [ ] **Brochure one-pager:** Usare [brochure-morel.md](brochure-morel.md) come base per PDF professionale

### 1.3 Template operativi (Giorno 3-5)

- [ ] **Template Report (Word/PDF):** struttura standard con foto termiche, priorita, costi, risparmi, bonus
- [ ] **Checklist Sopralluogo:** da [check-sopralluogo.md](check-sopralluogo.md)
- [ ] **Contratto B2B:** con clausola "3x Risparmio o Rimborsato" (da [brochure-morel.md](brochure-morel.md))
- [ ] **Script telefonico:** da [script-vendita.md](script-vendita.md)

---

## FASE 2 — Attivazione Rete (Giorni 6-15)

**Documenti:** [piano-3-contatti.md](piano-3-contatti.md), [sinergie-flipping.md](sinergie-flipping.md)

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
- [ ] **Script B2B (da [script-vendita.md](script-vendita.md)):** presentazione in 2 minuti, focus su ROI, chiedere la bolletta

---

## FASE 3 — Primi Check e Validazione (Giorni 16-30)

**Documenti:** [check-sopralluogo.md](check-sopralluogo.md), [dal-check-alla-soluzione.md](dal-check-alla-soluzione.md), [gemini-come-leggere-bollette.md](gemini-come-leggere-bollette.md)

### 3.1 Obiettivo: 3+ check paganti

- [ ] Eseguire check su immobile Marco (test gratuito)
- [ ] Check gratuito su condominio Amico 1
- [ ] **Target:** 3 check B2B a pagamento (€490 cad) entro giorno 30

### 3.2 Per ogni check

- [ ] Sopralluogo con le 7 fasi (checklist da [check-sopralluogo.md](check-sopralluogo.md))
- [ ] Analisi bollette (guida da [gemini-come-leggere-bollette.md](gemini-come-leggere-bollette.md))
- [ ] Report consegnato entro 48h
- [ ] Presentazione upsell: bonus ENEA (+€300), coordinamento lavori (+€1.500, 10% sui lavori)

### 3.3 Raccolta feedback

- [ ] Chiedere recensione Google a ogni cliente
- [ ] Chiedere 1 referral a ogni cliente
- [ ] Aggiornare CRM con esito chiamata/check

---

## FASE 4 — Consolidamento (Mesi 2-3)

**Documento:** [business-check-energetico-completo.md](business-check-energetico-completo.md) §13

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
