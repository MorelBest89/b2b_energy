import json

with open(r'C:\Users\marco\Projects\consulenza_energy\data\batches\batch_0.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = {}

for item in data:
    idx = str(item['index'])
    nome = item['nome']
    citta = item['citta']
    cat = item['categoria']
    tel = item['telefono']
    sito = item['sito']
    title = item['title']
    meta = item['meta']
    text = item['text'].lower()

    # ----- Scoring & description logic -----
    # Start with defaults
    punteggio = 5
    descrizione = ""
    note = ""

    # Detect keywords
    has_cucina = any(k in text for k in ['cucina', 'forno', 'pizza', 'chef', 'menu', 'piatti', 'ristorante'])
    has_hotel = any(k in text for k in ['hotel', 'camere', 'pernottamento', 'soggiorno', 'navetta'])
    has_hvac = any(k in text for k in ['climatizzato', 'aria condizionata', 'climatizzazione'])
    has_forno_legna = any(k in text for k in ['forno a legna', 'forno'])
    has_eventi = any(k in text for k in ['eventi', 'cerimonie', 'matrimoni', 'banchetti', 'catering'])
    has_piscina = any(k in text for k in ['piscina', 'pool'])
    has_spa = any(k in text for k in ['spa', 'benessere', 'sauna'])
    has_pane = any(k in text for k in ['pane', 'forno', 'pasticceria', 'lievitazione'])
    has_aperitivo = any(k in text for k in ['aperitivo', 'bar', 'cocktail', 'vino', 'birra'])
    has_giardino = any(k in text for k in ['giardino', 'esterno', 'dehors'])
    has_bimbi = any(k in text for k in ['bimbi', 'bambini', 'area giochi', 'parco giochi'])
    has_sale = any(k in text for k in ['sala', 'sale', 'coperti', 'posti'])
    has_delivery = any(k in text for k in ['delivery', 'take away', 'asporto', 'domicilio'])
    has_all_you_can = 'unlimited' in text or 'all you can' in text
    has_catena = any(k in nome.lower() for k in ['rossopomodoro', 'old wild west', 'fuddruckers', 'i love poke', 'iper'])

    # Special cases - wrong categories / broken sites
    is_wrong = False
    reason_wrong = ""

    # Index 8 - Miralago is a clinic for eating disorders
    if idx == '8':
        is_wrong = True
        reason_wrong = "centro disturbi alimentari, non ristorante"
    # Index 31 - Centro Gulliver is a social cooperative
    elif idx == '31':
        is_wrong = True
        reason_wrong = "cooperativa sociale Centro Gulliver, non ristorante"
    # Index 32 - Aria Srl is workwear
    elif idx == '32':
        is_wrong = True
        reason_wrong = "abbigliamento professionale DPI, non ristorante"
    # Index 93 - Holiday Inn Express hotel
    elif idx == '93' or 'holiday inn' in text or 'hiex-malpensa' in sito:
        is_wrong = True
        reason_wrong = "hotel Holiday Inn Express, non ristorante"
    # Index 54 - Fuddruckers domain points to Caguas (Porto Rico), not local
    elif idx == '54':
        is_wrong = True
        reason_wrong = "sito punta a Caguas Porto Rico, non pertinente"
    # Index 78 - Restaurant One is in Milano
    elif idx == '78':
        is_wrong = True
        reason_wrong = "ristorante a Milano, fuori zona"
    # Index 71 - hotel with restaurant
    elif idx == '71':
        is_wrong = False  # It's relevant - hotel with ristorante
    # Index 76 - hotel with restaurant
    elif idx == '76':
        is_wrong = False  # It's relevant - hotel with ristorante

    # Facebook/Instagram only sites
    is_social_only = ('facebook.com' in sito or 'instagram.com' in sito) and len(text.strip()) < 100
    # Empty/near-empty sites
    is_empty_site = len(text.strip()) < 150 and not is_social_only

    if is_wrong:
        info = {
            "descrizione": f"ERRORE CLASSIFICAZIONE: {nome} non è un ristorante/pizzeria. {reason_wrong}. Contatto da eliminare o ricategorizzare.",
            "note": "Escludere dal batch ristoranti. Contatto non pertinente.",
            "punteggio": 1
        }
    elif is_social_only:
        if idx == '15':
            info = {
                "descrizione": f"Gastronomia del Corso a Varese. Attiva su Instagram con 3.014 follower e 822 post. Gastronomia con cucina. Dimensioni stimate: piccola/media attività. Informazioni energetiche non disponibili dal profilo social. Presumibili attrezzature da gastronomia/ cucina professionale con forni e piani cottura.",
                "note": "Difficile profilazione: solo Instagram. Tentare contatto telefonico diretto. Check energetico base con termocamera.",
                "punteggio": 4
            }
        elif idx == '38':
            info = {
                "descrizione": f"Bianchi Bar a Varese. Bar con 455 follower Instagram. Attività di piccole dimensioni. Probabile attrezzatura da bar (macchina caffè, frigoriferi, piccola cucina).",
                "note": "Difficile profilazione: solo Instagram. Check energetico base con termocamera. Proporre audit gratuito bar.",
                "punteggio": 4
            }
        elif idx == '39':
            info = {
                "descrizione": f"Birbante a Varese, locale con aperitivi, pranzi, cene, eventi, diretta sport. Cucina espressa con menù lavoro a mezzogiorno. Attivo su Facebook con 1.174 like. Dimensioni stimate: medie. Attrezzatura: cucina professionale, frigoriferi, TV, impianto audio.",
                "note": "Menzionare risparmio su illuminazione e climatizzazione. Proporre audit energetico per ristorazione.",
                "punteggio": 5
            }
        elif idx == '43':
            info = {
                "descrizione": f"Break Bar Fusion Cafè a Varese. Bar con 1.377 like Facebook e 1.517 persone presenti. Attività principalmente serale. Dimensioni stimate: medie. Attrezzatura: bar professionale, piccola cucina, frigoriferi.",
                "note": "Solo Facebook. Check energetico base. Proporre audit illuminazione e climatizzazione.",
                "punteggio": 5
            }
        elif idx == '51':
            info = {
                "descrizione": f"DNA a Varese, pub con 1.126 like Facebook e 1.256 presenze. Locale serale. Dimensioni stimate: medie. Attrezzatura: bancone bar, frigoriferi, impianto audio/luci.",
                "note": "Proporre audit consumi serali. Illuminazione e climatizzazione sono voci importanti per pub.",
                "punteggio": 5
            }
        else:
            info = {
                "descrizione": f"{nome} a {citta}. Attività presente solo su social media (Facebook/Instagram). Dimensioni e attrezzature non stimabili dal profilo. Categoria: {cat}.",
                "note": "Difficile profilazione: solo social. Tentare contatto telefonico per verifica. Check energetico base.",
                "punteggio": 3
            }
    elif is_empty_site:
        info = {
            "descrizione": f"{nome} a {citta}. Sito web quasi vuoto o non accessibile. Poche informazioni disponibili. Categoria: {cat}. Telefono: {tel}.",
            "note": "Sito non informativo. Contattare direttamente per profilazione. Check energetico base con termocamera.",
            "punteggio": 2
        }
    else:
        # Generate description and notes based on content analysis
        has_pizza = any(k in text for k in ['pizza', 'pizzeria', 'forno a legna'])
        has_pesce = any(k in text for k in ['pesce', 'pescato', 'mare', 'crudo'])
        has_carne = any(k in text for k in ['carne', 'griglia', 'bistecca', 'tagli'])
        has_sushi = any(k in text for k in ['sushi', 'sashimi', 'giapponese', 'fusion', 'nip']) or 'sushi' in nome.lower()
        has_asia = any(k in text for k in ['cinese', 'thai', 'vietnamita', 'asiatic'])
        has_pane_cotto = 'tandoori' in text or 'tandoor' in text
        
        # Estimate size
        size = "media"
        if has_sale and ('150' in text or '200' in text or '300' in text):
            size = "grande"
        elif has_hotel:
            size = "media/grande"
        elif has_eventi and has_sale:
            size = "media/grande"
        elif has_giardino and has_sale:
            size = "media"
        elif has_delivery or 'asporto' in text:
            size = "piccola/media"
            
        # Score calculation
        score = 5  # base for ristorante with content
        
        # Ristoranti/pizzerie with cucina + HVAC + eventi = higher score
        if has_cucina and has_hvac and has_eventi:
            score = 9
        elif has_cucina and has_hvac:
            score = 8
        elif has_cucina and has_eventi:
            score = 7
        elif has_cucina and has_forno_legna:
            score = 7
        elif has_cucina:
            score = 6
        elif has_aperitivo:
            score = 5
        elif has_pizza:
            score = 6
            
        # Hotels with restaurant get higher scores
        if has_hotel and has_cucina:
            score = max(score, 8)
        if has_hotel and has_cucina and has_piscina:
            score = max(score, 9)
            
        # Catene = medium score (standardizzati)
        if has_catena:
            score = min(score, 6)
            
        # Pizza delivery only = lower
        if has_delivery and not has_cucina and not has_eventi:
            score = min(score, 5)
            
        # All-you-can-eat large sushi places = good potential
        if has_all_you_can and has_sushi:
            score = max(score, 7)

        # Build description
        parts = []
        parts.append(f"{nome} a {citta}.")
        
        if has_hotel:
            parts.append(f"Struttura ricettiva con ristorante interno.")
        elif has_pizza and has_cucina:
            parts.append(f"Ristorante con pizzeria.")
        elif has_pizza:
            parts.append(f"Pizzeria.")
        elif has_sushi:
            parts.append(f"Ristorante di cucina giapponese/asiatica.")
        else:
            parts.append(f"Ristorante.")
            
        # Key features
        features = []
        if has_hvac: features.append("climatizzato")
        if has_forno_legna: features.append("forno a legna")
        if has_eventi: features.append("organizza eventi/cerimonie")
        if has_giardino: features.append("giardino esterno")
        if has_bimbi: features.append("area bimbi")
        if has_piscina: features.append("piscina")
        if has_delivery: features.append("delivery/take away")
        if has_all_you_can: features.append("menu unlimited")
        if has_pane_cotto: features.append("tandoor/cucina tradizionale indiana")
        if features:
            parts.append(f"Caratteristiche: {', '.join(features)}.")
            
        parts.append(f"Dimensioni stimate: {size}.")
        parts.append(f"Attrezzature energetiche: cucina professionale, forni, frigoriferi" + 
                    (", climatizzazione" if has_hvac else "") + 
                    (", forno a legna" if has_forno_legna else "") + ".")
        
        equip = ["cucina professionale", "forni", "frigoriferi"]
        if has_hvac: equip.append("climatizzazione")
        if has_forno_legna: equip.append("forno a legna")
        if has_eventi or has_sale: equip.append("impianto illuminazione esteso")
        if has_piscina: equip.append("piscina")
        parts[-1] = f"Attrezzature energetiche: {', '.join(equip)}."
        
        descrizione = " ".join(parts)
        if len(descrizione) > 500:
            descrizione = descrizione[:497] + "..."

        # Build notes
        note_parts = []
        if has_hvac:
            note_parts.append("Menzionare risparmio su climatizzazione")
        if has_forno_legna:
            note_parts.append("Proporre check efficienza forno a legna")
        if has_aperitivo and not has_cucina:
            note_parts.append("Focus su illuminazione e frigoriferi")
        if has_pizza:
            note_parts.append("Proporre check forno pizza")
        if has_eventi:
            note_parts.append("Audit consumi eventi e sala")
        if has_hotel:
            note_parts.append("Check camere + climatizzazione centralizzata")
        if has_piscina:
            note_parts.append("Proporre check pompe piscina")
        if has_delivery:
            note_parts.append("Verifica efficienza trasporto/delivery")
        if has_sushi:
            note_parts.append("Focus su celle frigorifere")
        if has_pesce:
            note_parts.append("Verifica celle frigorifere pesce")
        if has_bimbi:
            note_parts.append("Cenno a comfort area bimbi (clima)")
        if has_catena:
            note_parts.append("Proposta multi-sede, risparmio su scala")
            
        if not note_parts:
            note_parts.append("Check energetico base con termocamera")
            
        note = ". ".join(note_parts) + "."
        if len(note) > 300:
            note = note[:297] + "..."

        info = {
            "descrizione": descrizione,
            "note": note,
            "punteggio": score
        }

    # ---- OVERRIDES for specific cases based on deep content analysis ----
    
    # Mareamore - ristorante pesce, area bimbi
    if idx == '0':
        info = {
            "descrizione": "Mareamore a Varese, ristorante di pesce con area bimbi dedicata. Locale con cucina professionale, frigoriferi per conservazione pesce fresco, forni. Dimensioni stimate: medie. Climatizzazione presente. Atmosfera familiare con servizio di prenotazione online.",
            "note": "Menzionare risparmio su climatizzazione e conservazione pesce. Proporre check frigoriferi e illuminazione LED in sala.",
            "punteggio": 7
        }
    elif idx == '1':
        info = {
            "descrizione": "Circolo di Capolago a Varese, griglieria con ampia selezione di birre. Menù ricco: costine, stinco, hamburger. Organizza eventi. Sale interne e vista lago. Cucina professionale con griglie, forni, frigoriferi. Dimensioni stimate: medie/grandi. Climatizzazione verosimile.",
            "note": "Menzionare risparmio su griglie e climatizzazione. Audit cucina e illuminazione sale. Proporre check efficienza energetica attrezzature cottura.",
            "punteggio": 8
        }
    elif idx == '2':
        info = {
            "descrizione": "La Terrazza a Varese, ristorante gourmet con oltre 20 anni di esperienza (dal 1998). Cucina di pesce e carne in ambiente elegante. Dispone di saletta interna. Dimensioni stimate: medie. Attrezzature: cucina professionale, frigoriferi, forni. Climatizzato. Ideale per cene romantiche e business.",
            "note": "Menzionare esperienza ventennale. Proporre audit efficienza cucina e relamping LED per atmosfera elegante.",
            "punteggio": 7
        }
    elif idx == '3':
        info = {
            "descrizione": "Vibes a Varese, wine bar con cocktail e tapas. Aperto da martedì a domenica, orari prevalentemente serali. Sabato e domenica anche pranzo. Locale elegante con atmosfera curata. Dimensioni stimate: piccole/medie. Attrezzatura: bancone bar, frigoriferi vini, piccola cucina per tapas.",
            "note": "Focus su illuminazione d'atmosfera e refrigerazione vini. Proporre audit consumi bar.",
            "punteggio": 5
        }
    elif idx == '5':
        info = {
            "descrizione": "Le Arcate a Varese, ristorante e pizzeria dal 1986 con cucina mediterranea tradizionale. Locale rustico e accogliente su due sale. Forno a legna per pizze. Dimensioni stimate: medie. Attrezzature: cucina professionale, forno a legna, frigoriferi.",
            "note": "Proporre check forno a legna e efficienza cottura. Menzionare risparmio su illuminazione e climatizzazione.",
            "punteggio": 7
        }
    elif idx == '6':
        info = {
            "descrizione": "Tana D'Orso a Varese, ristorante elegante dal 2005 sviluppato su due piani con sala da 150 coperti e giardino esterno. Specializzato in cucina lombarda e piemontese. Organizza eventi e cerimonie con impianto audio-video. Dimensioni stimate: grandi. Attrezzature: cucina professionale, forni, frigoriferi, climatizzazione, impianto AV.",
            "note": "Cliente di alto potenziale: 150 coperti, eventi, due piani. Audit completo consumi: climatizzazione, cucina, illuminazione sale. Proporre monitoraggio energetico continuo.",
            "punteggio": 9
        }
    elif idx == '7':
        info = {
            "descrizione": "Mikuna a Varese, ristorante peruviano autentico nel centro città. Specialità: ceviche, lomo saltado, causa. Cucina etnica con ingredienti freschi. Dimensioni stimate: piccole/medie. Attrezzature: cucina professionale, frigoriferi, forni.",
            "note": "Check energetico base con termocamera. Proporre audit illuminazione e frigoriferi.",
            "punteggio": 5
        }
    elif idx == '10':
        info = {
            "descrizione": "Mizu Fusion a Varese, ristorante giapponese con cucina fusion. Offre corsi di cucina, catering, affitto sale per eventi. Dispone di grande parcheggio gratuito. Dimensioni stimate: medie/grandi. Attrezzature: cucina professionale, celle frigorifere, forni. Possibili più sale.",
            "note": "Multi-servizio (corsi, catering, eventi) = consumi elevati. Focus su celle frigorifere e climatizzazione sale.",
            "punteggio": 8
        }
    elif idx == '11':
        info = {
            "descrizione": "Volo a Vela sul Lago di Varese, ristorante con pizzeria e forno a legna. Cucina mediterranea, cerimonie e banchetti. Aperto tutti i giorni. Dimensioni stimate: medie/grandi. Attrezzature: cucina professionale, forno a legna, frigoriferi, climatizzazione.",
            "note": "Forno a legna = check efficienza. Cerimonie = consumi sala elevati. Audit completo consigliato.",
            "punteggio": 8
        }
    elif idx == '12':
        info = {
            "descrizione": "Haru Japan Fusion a Varese, ristorante giapponese/asiatico con spazi climatizzati. Cucina vegana e senza glutine. Organizza eventi privati. Wi-Fi, accesso disabili. Aperto 6/7. Dimensioni stimate: medie. Attrezzature: cucina professionale, frigoriferi, climatizzazione.",
            "note": "Spazi climatizzati citati nel sito = cliente sensibile al tema. Proporre audit climatizzazione e illuminazione.",
            "punteggio": 7
        }
    elif idx == '16':
        info = {
            "descrizione": "Haveli a Varese, ristorante indiano con cucina tandoori. Menu online con ampia scelta: tandoori, curry, riso basmati, birre e vini indiani. Delivery e take away. Dimensioni stimate: medie. Attrezzature: forno tandoor, cucina professionale, frigoriferi.",
            "note": "Forno tandoor = consumo elevato. Proporre check efficienza forno e frigoriferi. Audit consumi cottura.",
            "punteggio": 7
        }
    elif idx == '17':
        info = {
            "descrizione": "I Love Poke, catena di fast food healthy con punto vendita presso Le Corti a Varese. Concept hawaiian poke bowls. Delivery e take away. Dimensioni stimate: piccole (chiosco/negozio in centro commerciale). Attrezzature: banco preparazione, frigoriferi esposizione.",
            "note": "Punto vendita in centro commerciale. Consumi limitati. Check base frigoriferi e illuminazione.",
            "punteggio": 4
        }
    elif idx == '18':
        info = {
            "descrizione": "Iper La Grande I a Varese, grande centro commerciale con supermercato, ristò, pizzeria, ottica, parafarmacia e negozi. Struttura di grandi dimensioni con food court. Attrezzature: cucine industriali, forni, celle frigorifere, illuminazione estesa, climatizzazione centralizzata.",
            "note": "Cliente GRANDE: centro commerciale. Consumi energetici elevatissimi. Proporre audit multi-reparto: illuminazione, climatizzazione, celle frigorifere.",
            "punteggio": 9
        }
    elif idx == '21':
        info = {
            "descrizione": "Rom'Antica a Varese centro, pizzeria alla romana al taglio. Pizza croccante cotta in teglia, supplì. Aperta tutti i giorni 09:00-22:00. Dimensioni stimate: piccole/medie. Attrezzature: forno teglia, frigoriferi esposizione, banco vendita.",
            "note": "Forno pizza teglia = check efficienza. Orario continuato = consumi costanti. Audit base forno e illuminazione.",
            "punteggio": 5
        }
    elif idx == '22':
        info = {
            "descrizione": "Rossopomodoro all'aeroporto di Malpensa (Terminal 1), catena napoletana di pizzerie. Aperto tutti i giorni 11:00-22:00. Location aeroportuale ad alto traffico. Dimensioni stimate: medie. Attrezzature: cucina professionale, forni pizza, frigoriferi. Standard catena.",
            "note": "Location aeroportuale = orari estesi. Contatto regionale per multi-sede. Audit standard catena.",
            "punteggio": 6
        }
    elif idx == '23':
        info = {
            "descrizione": "Dim Sum Ye a Varese, ristorante di cucina asiatica (dim sum). Sito web minimale con solo intestazione. Dimensioni e attrezzature non stimabili con precisione. Presumibile cucina professionale con wok e frigoriferi.",
            "note": "Sito non informativo. Contattare direttamente. Check energetico base con termocamera.",
            "punteggio": 2
        }
    elif idx == '24':
        info = {
            "descrizione": "El Crocante a Varese, ristorante peruviano. Attivo su Facebook con 1.326 like e 832 presenze. Dimensioni stimate: piccole/medie. Attrezzature: cucina professionale, frigoriferi, forni.",
            "note": "Solo Facebook. Tentare contatto telefonico. Check energetico base.",
            "punteggio": 4
        }
    elif idx == '29':
        info = {
            "descrizione": "La Noce a Mercallo (VA), ristorante sulla collina vicino al Lago di Comabbio. Dal 1991, cucina tradizionale con pesce di lago/mare. Climatizzato, con parco giochi bimbi e tendaggio esterno estivo. Specializzato in eventi: battesimi, matrimoni, cene aziendali. Chef Gianluca. Dimensioni stimate: medie/grandi.",
            "note": "Cliente di pregio: eventi, climatizzato, parco giochi. Audit completo: climatizzazione, cucina, illuminazione. Menzionare check parco giochi e tendaggio (consumi estivi).",
            "punteggio": 8
        }
    elif idx == '36':
        info = {
            "descrizione": "Bar Social a Varese, bar con cucina, edicola e servizi urbani. Musica dal vivo, eventi culturali. Punto di aggregazione sociale. Dimensioni stimate: medie. Attrezzature: cucina professionale, bancone bar, frigoriferi, impianto audio/luci, edicola.",
            "note": "Multi-servizio (bar+cucina+edicola+eventi) = consumi vari. Audit consumi generali. Proporre illuminazione LED e climatizzazione.",
            "punteggio": 6
        }
    elif idx == '44':
        info = {
            "descrizione": "Cento46 a Varese, ristorante e pizzeria con cucina innovativa. Utilizza prodotti del territorio italiano. Via Daverio 146. Dimensioni stimate: medie. Attrezzature: cucina professionale, forno pizza, frigoriferi.",
            "note": "Check forno pizza e frigoriferi. Proporre audit consumi cucina e illuminazione.",
            "punteggio": 6
        }
    elif idx == '45':
        info = {
            "descrizione": "C'Era Una Volta a Varese, ristorante con pizzeria ai piedi del Sacromonte. Due ampie sale interne e giardino coperto. Cucina tradizionale carne e pesce, pizza, selezione vini. Serate a tema. Dimensioni stimate: medie/grandi. Attrezzature: cucina professionale, forno pizza, frigoriferi, climatizzazione.",
            "note": "Due sale + giardino = superficie significativa. Audit climatizzazione e illuminazione. Menzionare risparmio su gestione eventi/serate.",
            "punteggio": 8
        }
    elif idx == '46':
        info = {
            "descrizione": "Chicco e Spiga a Varese, pizzeria artigianale. Pizze classiche, gourmet, bianche e panini con impasto pizza. Via Giulio Uberti 1. Dimensioni stimate: piccole. Attrezzature: forno pizza, frigoriferi.",
            "note": "Check forno pizza. Audit base consumi. Proporre relamping LED.",
            "punteggio": 5
        }
    elif idx == '53':
        info = {
            "descrizione": "Felicità Sushi a Varese, ristorante sushi. Presenza solo su Quandoo (piattaforma prenotazioni). Dimensioni e attrezzature non verificabili dal sito. Presumibile cucina giapponese con frigoriferi.",
            "note": "Sito non informativo. Contattare direttamente. Check energetico base.",
            "punteggio": 2
        }
    elif idx == '59':
        info = {
            "descrizione": "Il Convivio del Sacro Monte a Varese, panineria e gastronomia artigianale. Panini gourmet, vegetariani, vegani, torte artigianali. Menù stagionale (polenta e cioccolata calda inverno). Location turistica sul Sacro Monte. Dimensioni stimate: piccole. Attrezzature: banco gastronomia, frigoriferi, forno.",
            "note": "Location turiva = stagionalità consumi. Check frigoriferi e illuminazione. Audit base.",
            "punteggio": 4
        }
    elif idx == '62':
        info = {
            "descrizione": "Osteria Irma a Varese (Campo dei Fiori, 1100m quota). Cucina territoriale, pasta fresca, carne. Nata nel 2017 dalla storica Pensione Irma del 1949. Prodotti locali stagionali. Location immersa nel Parco Regionale. Dimensioni stimate: medie. Attrezzature: cucina professionale, forni, frigoriferi.",
            "note": "Location montana = riscaldamento voce importante. Audit isolamento e climatizzazione. Proporre efficienza riscaldamento.",
            "punteggio": 6
        }
    elif idx == '64':
        info = {
            "descrizione": "K Kaiseki a Varese (Viale Milano 5), ristorante sushi con formula unlimited. Pranzo feriale 16,90€, cena 30€. Take away. Promozioni settimanali. Parcheggio gratuito. Dimensioni stimate: medie/grandi. Attrezzature: cucina giapponese, celle frigorifere, forni, banco sushi.",
            "note": "Formula unlimited = alto volume coperti. Celle frigorifere = consumo continuo. Audit completo consumi. Proporre monitoraggio.",
            "punteggio": 7
        }
    elif idx == '65':
        info = {
            "descrizione": "Kobe Sushi a Varese, ristorante fusion asiatico (giapponese, cinese, thai). Formula All You Can Eat e à la carte. Sconto 20% asporto. Dimensioni stimate: medie/grandi. Attrezzature: cucina professionale, celle frigorifere, forni, banco sushi.",
            "note": "All you can eat = volumi elevati. Frigoriferi e cottura continua. Audit consumi e illuminazione.",
            "punteggio": 7
        }
    elif idx == '66':
        info = {
            "descrizione": "La Cucina di Altamura a Varese, ristorante con concept 'micro porzioni a peso'. Specialità pugliesi al banco. Birre e vini solo pugliesi. Aperto lun-ven 08:00-23:00, sab 12:00-23:00. Dimensioni stimate: medie. Attrezzature: banco esposizione, cucina professionale, frigoriferi, forni.",
            "note": "Concept micro porzioni = banco sempre attivo. Audit consumi banco refrigerato e illuminazione. Proporre check efficienza.",
            "punteggio": 6
        }
    elif idx == '68':
        info = {
            "descrizione": "Ristorante Pizzeria Marialia a Capiago Intimiano (CO), dal 1980. Aria condizionata, angolo bambini, parcheggio, take away, Wi-Fi, animali ammessi. Accessibile. Dimensioni stimate: medie. Attrezzature: cucina professionale, forno pizza, frigoriferi, climatizzazione.",
            "note": "Aria condizionata e angolo bimbi citati. Audit climatizzazione e forno pizza. Proporre risparmio su climatizzazione.",
            "punteggio": 7
        }
    elif idx == '71':
        info = {
            "descrizione": "Hotel Cervo a Somma Lombardo (Malpensa), hotel con ristorante interno a 1km dall'aeroporto. Navetta aeroportuale, WiFi gratuito, camere con bagno. Ristorante interno all'hotel. Dimensioni stimate: medie. Attrezzature: cucina professionale, frigoriferi, climatizzazione camere e sala, lavanderia.",
            "note": "Struttura ricettiva: check climatizzazione camere + ristorante. Proporre audit integrato hotel. Lavanderia = consumo significativo.",
            "punteggio": 8
        }
    elif idx == '74':
        info = {
            "descrizione": "Boa Vida a Somma Lombardo, churrascaria brasiliana con rodizio. Oltre 10 tagli di carne (manzo, pollo, maiale, agnello). Caipirinha e cocktail. Punteggio Google 5.0. Dimensioni stimate: medie. Attrezzature: griglie professionali, forni, frigoriferi, banco carne.",
            "note": "Griglie consumano molto. Audit efficienza cottura e refrigerazione carne. Proporre check consumi griglie.",
            "punteggio": 7
        }
    elif idx == '76':
        info = {
            "descrizione": "Hotel Ristorante La Perla a Varallo Pombia, hotel 4 stelle immerso nel parco con piscina. Ristorante e bar interni, giardino, navetta. Lavanderia, parcheggio custodito. Vicino Lago Maggiore. Dimensioni stimate: grandi. Attrezzature: cucina professionale, frigoriferi, climatizzazione camere, piscina, lavanderia.",
            "note": "Hotel 4 stelle con piscina = cliente TOP. Audit completo: climatizzazione camere, pompe piscina, lavanderia, cucina. Proporre monitoraggio continuo.",
            "punteggio": 9
        }
    elif idx == '77':
        info = {
            "descrizione": "Old Wild West a Somma Lombardo (Via Milano 156), ristorante steakhouse della catena. Carne alla griglia, hamburger. Ordinazione online, asporto. TV, eventi, animali ammessi. Parcheggio. Dimensioni stimate: medie/grandi. Orari 12:00-15:00 e 18:30-22:00/22:30.",
            "note": "Catena nazionale = contatto regionale. Griglie e frigoriferi consumi principali. Audit standard catena.",
            "punteggio": 6
        }
    elif idx == '79':
        info = {
            "descrizione": "Sapori d'Italia a Gallarate (VA), ristorante pizzeria dal 2008. Cucina tradizionale italiana con eccellenze nord-sud. Ambiente familiare. Dimensioni stimate: medie. Attrezzature: cucina professionale, forno pizza, frigoriferi.",
            "note": "Check forno pizza e frigoriferi. Proporre audit consumi e relamping LED.",
            "punteggio": 6
        }
    elif idx == '81':
        info = {
            "descrizione": "Pipi e Patate a Gallarate (VA), autentica cucina calabrese. Ingredienti tipici calabresi da fornitori selezionati. Attività a conduzione familiare con tradizione dal 1974. Dimensioni stimate: medie. Attrezzature: cucina professionale, forni, frigoriferi.",
            "note": "Cucina tradizionale = forni e piani cottura. Audit base consumi. Proporre check efficienza attrezzature.",
            "punteggio": 6
        }
    elif idx == '83':
        info = {
            "descrizione": "Flavour Of India a Gallarate, ristorante indiano. Sito web minimale con solo intestazione e link menu. Dimensioni e attrezzature non verificabili. Presumibile cucina indiana con forno tandoor e frigoriferi.",
            "note": "Sito non informativo. Contattare direttamente. Proporre check forno tandoor (consumo elevato).",
            "punteggio": 3
        }
    elif idx == '85':
        info = {
            "descrizione": "Birrificio Settimo a Somma Lombardo, birrificio artigianale dal 2010 con craft house. Produzione birra in loco (3 linee: Triskell, Bulli, Pink Kriek). Pizze leggere, taglieri, cucina birraria. Prenotazione online. Dimensioni stimate: medie. Attrezzature: impianto produzione birra (consumo elevato), cucina professionale, forno pizza, frigoriferi.",
            "note": "IMPIANTO PRODUZIONE BIRRA = consumo energetico molto alto. Cliente prioritario. Audit completo: produzione, refrigerazione, cottura.",
            "punteggio": 9
        }
    elif idx == '86':
        info = {
            "descrizione": "Lomitos a Gallarate, ristorante argentino. Sito web quasi vuoto con poche informazioni. Solo intestazione e messaggio generico. Dimensioni e attrezzature non stimabili. Presumibile cucina con griglie per carne argentina.",
            "note": "Sito non informativo. Contattare direttamente. Verificare presenza griglie e consumi.",
            "punteggio": 2
        }
    elif idx == '90':
        info = {
            "descrizione": "La Pizzeria Di a Somma Lombardo, Marnate e Ferno, pizza senza glutine certificata AIC. Tre sedi, ordinazione via app, consegna a domicilio in 30 minuti (2,50€). Aperti 7/7 18:00-22:00. Dimensioni stimate: piccole/medie per sede. Attrezzature: forni elettrici, frigoriferi, impastatrici.",
            "note": "Tre sedi = potenziale multi-sito. Forni elettrici = check efficienza. Proporre audit su tutte le sedi.",
            "punteggio": 7
        }

    results[idx] = info

# Write output
output_path = r'C:\Users\marco\Projects\consulenza_energy\data\batches\result_0.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Done! Processed {len(results)} contacts. Output: {output_path}")

# Summary
scores = [v['punteggio'] for v in results.values()]
avg = sum(scores) / len(scores)
print(f"\nScore distribution:")
for s in range(1, 11):
    cnt = scores.count(s)
    if cnt > 0:
        print(f"  Score {s}: {cnt} contatti")
print(f"\nScore medio: {avg:.1f}")
print(f"Totali: {len(results)} contatti")
