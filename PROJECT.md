# Cronologia di Arda: documento di passaggio

Sito fan non commerciale su Tolkien (Il Signore degli Anelli, Lo Hobbit, Il Silmarillion e altri scritti). Lingua del sito e dei testi: **italiano**.

Questo file riassume obiettivi, decisioni prese, stato del codice e prossimi passi. Il sito è `index.html` con il codice in `js/` e i dati in `data/`. Leggi prima tutto il file, poi apri `index.html`.

## 1. Obiettivo: tre funzioni

1. **Timeline completa** di tutta la storia raccontata da Tolkien, non solo il Signore degli Anelli: tutte le Ere (Lampade, Alberi, Prima, Seconda, Terza, e in prospettiva Quarta).
2. **Alberi genealogici** di tutti i personaggi principali.
3. **Mappe interattive** della Terra di Mezzo, di Númenor e di Valinor. Interattive significa che mostrano dove si sono svolti eventi e battaglie e come la geografia cambia nel tempo.

Si parte dalla timeline. Le altre due funzioni vanno progettate in modo che condividano i dati con la timeline.

## 2. Decisioni già prese dall'utente

- **Interfaccia timeline:** cerchio con gli anni e le note intorno, ispirato all'infografica "Timeline of the One Ring" di lotrproject.com (Emil Johansson). Il cerchio è la linea del tempo, la mappa sta **al centro del cerchio**, e dall'evento sull'anello parte una linea fino al luogo sulla mappa.
- **Variante grafica scelta:** "infografica" (file `cerchio-a-infografica` nella storia del progetto; il cerchio attuale ne deriva). Alternativa non scelta ma non bocciata: la variante "inchiostro", non più nel repository.
- **Titolo:** "Cronologia di Arda". Il titolo precedente "Il cerchio del tempo" è stato bocciato.
- **Responsive vero, non solo mobile:** su schermo largo il cerchio diventa grande nella colonna di sinistra e a destra stanno titolo, descrizione e pulsanti. Su schermo stretto colonna singola.
- **Interazione:** niente movimenti automatici legati allo scroll (una versione precedente scattava ed è stata scartata). Selezione con tocco o clic, pulsanti Precedente e Successivo, frecce della tastiera.
- **Mappe:** disegnate da zero, mai riprodotte da mappe ufficiali. La mappa al centro cambia con l'era selezionata, perché la geografia cambia (Beleriand sprofonda, Númenor esiste solo nella Seconda Era, Valinor viene sottratta al mondo).

## 3. Design

Riferimento: infografica con fondo neutro, un solo carattere sans geometrico, linee sottili, arco marrone scuro e arco blu, un grosso numero in blu come dato chiave.

- **Font:** Raleway (300, 400, 600, 800), unico carattere.
- **Titolo:** maiuscolo, peso 300, spaziatura larga. Niente parole in grassetto isolate dentro il titolo.
- **Colori (chiaro):** sfondo `#eeeeec`, testo `#2a211d`, silenzioso `#7a726b`. Ere: Lampade `#cdbf8f`, Alberi `#9aa38a`, Prima `#9b2f28`, Seconda `#3a2b25`, Terza `#2f5a8a`. Esistono i valori per il tema scuro (`prefers-color-scheme`).
- **Dato chiave:** "7052 anni raccontati", in blu, a imitazione di "7 ring bearers 4860 years".

**Da evitare, perché l'utente li ha bocciati come "AI slop":** schede tutte uguali, palette pergamena marrone e crema, un solo elemento evidenziato a caso, caratteri calligrafici ornamentali (Almendra bocciato), navigazione che si muove da sola.

## 4. Stato del codice (`index.html` e `js/`)

Pagina HTML singola, JavaScript senza librerie, tutto in SVG. Nessun build.

- `SEG`: archi delle ere. Lampade e Alberi hanno ampiezza fissa (14° ciascuno, non in scala). Prima, Seconda e Terza Era hanno ampiezza **proporzionale agli anni** (590, 3441, 3021; totale 7052). Apertura di 20° in alto.
- `EV`: 16 eventi di esempio nel formato `[indiceEra, etichettaData, titolo, descrizione, annoNumerico]`.
- `AN`: angolo di ogni evento. Gli eventi troppo vicini vengono distanziati di almeno 3,6° per poterli toccare.
- `MP`: coordinate sulla mappa (spazio 400×400) dei cinque eventi della Terza Era. `MT`, `LB`, `mapG()`: montagne, nomi e disegno della mappa schematica della Terra di Mezzo.
- `draw()` ridisegna tutto a ogni selezione. Nel centro: mappa se l'era è la Terza, altrimenti data e titolo.

### Limiti noti

- La mappa esiste solo per la Terza Era ed è uno schema approssimato, non fedele.
- Sul telefono i nomi sulla mappa sono illeggibili. Previsto: toccare la mappa per aprirla a schermo intero.
- Solo 16 eventi. Quarta Era assente.
- Le date degli eventi vanno **verificate** contro le fonti (Appendice B del Signore degli Anelli, Il Silmarillion) prima della pubblicazione.
- Scelta ancora da fare: se l'evento selezionato debba avere richiami con testo intorno al cerchio come nell'infografica originale, invece del solo pannello a destra.

## 5. Modello dati proposto

Un unico dataset (JSON) che alimenti timeline, mappe e alberi:

- `eras`: id, nome, durata in anni, scala reale sì o no, colore, mappa associata.
- `events`: id, era, data (anno, giorno e mese se noti), titolo, descrizione (parole proprie), tipo (battaglia, fondazione, distruzione…), luogo, personaggi, fonte.
- `places`: id, nome, coordinate per ciascuna mappa, regione.
- `people`: id, nome, razza, nascita, morte, genitori, coniugi.
- `maps`: una per periodo, con livelli (coste, montagne, foreste, luoghi) e intervallo di validità.

## 6. Prossimi passi consigliati

1. Impostare un progetto vero (sito statico, build semplice) e spostare i dati degli eventi in file JSON.
2. Allargare il dataset della timeline e verificare le date.
3. Disegnare le mappe delle altre ere, partendo da Beleriand (Prima Era), poi Númenor e Terra di Mezzo (Seconda), Aman/Valinor (Lampade e Alberi).
4. Funzioni della timeline: zoom, ricerca, filtri per personaggio e luogo, apertura a schermo intero della mappa su telefono.
5. Alberi genealogici (grafo, non albero semplice: matrimoni incrociati tra dinastie).
6. Mappe interattive con cursore temporale che cambia confini ed eventi.

## 7. Contenuti e diritti

- Sito fan non commerciale. Mappe ufficiali (in particolare quelle di Christopher Tolkien) e testi sono protetti: **non copiarli**.
- Mappe e descrizioni vanno prodotte da zero e in parole proprie.
- Anche il lettering molto tolkieniano delle infografiche di riferimento va evitato: servirà un'identità grafica propria.

## 8. Come lavora l'utente

Vuole risposte dirette, senza convenevoli e senza adulazione. Preferisce che tu sia critico e lo sfidi quando serve, invece di dargli ragione per forza. Quando una scelta grafica gli sembra generica lo dice senza giri di parole: prendilo come indicazione, non come un problema di tono.

## 9. Stato a novembre 2026 (sessione OpenCode)

- **Decisioni confermate**: v1 solo Terza Era, cerchio con l'intera era in scala reale (la tabella `eras` sarà completa da subito, gli eventi solo Terza). Quarta Era rimandata. Cosmologia completa rimandata alla fase di apertura delle altre Ere. Mappe: dettaglio geografico alto senza sacrificare la leggibilità.
- **Grafica scelta: «Atlante»** (in `proposte/atlante.html`). Le altre due proposte («Editoriale», «Notturno») restano in `proposte/` come riferimento scartato. Giudizio condiviso: Atlante è la più sobria; da affinare con dettagli per non risultare fredda.
- **Fase 0 completata**: progetto strutturato (git attivo). `index.html` + `css/main.css` + `js/circle.js` (disegno del cerchio) + `js/data.js` (dataset). **Nota tecnica**: i dati nascono come YAML in `data/eventi/`; `tools/build_data.py` li valida e genera `js/data.js` con costanti globali (non JSON puro), così la pagina funziona anche aprendola direttamente da file senza server. Lo stesso build produce `build/arda.sqlite`, `build/indexes.json`, `build/schede-terza-era.md` e `build/rapporto.md`. Serve PyYAML (`requirements.txt`).
- **Fonti**: in `fonti/` (ignorata da git, testi protetti) ci sono LoTR con Appendici (Bompiani 2004) e Lo Hobbit in .epub. Estrazione del testo dell'Appendice B in `fonti/estrazione/`. Serve anche Il Silmarillion per la fase 4.
- **Repository remota**: `github.com/just-a-macaco/cronologia-arda` (pubblica, per GitHub Pages gratuito). Autenticazione via chiave SSH `~/.ssh/ed25519_github_arda` (config in `~/.ssh/config`). Email dei commit: `356642525+just-a-macaco@users.noreply.github.com` (storia riscritta prima del primo push). Backup spinto e verificato: `fonti/` non è online.
- **Fase 1 completata**: dataset Terza Era di **51 eventi**, ogni data verificata riga per riga sull'estratto dell'Appendice B in `fonti/estrazione/appendice-b.txt`. Fonte citata per evento (`source`: «Il calcolo degli anni», «I Grandi Anni», «Giorni principali»). Il motore (`js/circle.js`) ora gestisce i fitti finali con due file di punti alternate (MIN 2°, fila esterna a +20px): senza questo la coda 2941–3021 si compenetrerebbe. Correzioni rispetto alle prime 21 date: Arnor/Gondor non nascono nell'Anno 1 (era Seconda Era), l'ombra sul Bosco è del 1050 ma Dol Guldur si scopre c. 1100, l'omicidio di Déagol è il 2463 (non 2470), a Celebrant gli avversari erano Orchi ed Esterling, Sauron nel 2951 torna a Mordor (non a Dol Guldur).
- **Convenzioni dei nomi**: da ora vivono in `glossario.md`. Regola unica, senza eccezioni: **se l'epub Bompiani 2004 dice X, il sito dice X**. Nuove voci si aggiungono lì, non sparse nei testi.
- **Fase 1 estesa (novembre 2026)**: le 51 schede brevi sono diventate **61 schede complete** in YAML, con data e precisione, luoghi, partecipanti con ruolo ed esito, testo breve e testo lungo, fonti e certezza. Sette eventi del dataset originale contenevano più avvenimenti distinti e sono stati separati (per esempio `anello-bilbo` → Consiglio su Dol Guldur, morte di Smaug, Cinque Eserciti); è stata aggiunta la «Festa inattesa» del 2941. Gli ID storici restano invariati dove possibile, così il cerchio continua a funzionare. Nomi corretti sull'epub: Carrieri (non Aurighe), Rifugi Oscuri (non Porti Grigi), Dàin, Thràin, Nain, Eorl, Rath Dinen, Nevecrino, Grima Vermilinguo.
- **Anagrafica dei luoghi (novembre 2026)**: creato `data/luoghi.yaml` con **77 luoghi** (ID, nome, tipo, alias, gerarchia `dentro`, descrizione). Il build valida ID doppi, alias in conflitto e gerarchie circolari, e produce `build/luoghi.json` più `build/rapporto-luoghi.md`. Le 77 schede coprono **tutti gli 85 nomi** di luogo citati dagli eventi: i nomi in più sono alias dello stesso luogo (Minas Anor/Minas Tirith, Imladris/Gran Burrone, Khazad-dûm/Moria, Montagna Solitaria/Erebor, Mithlond/Rifugi Oscuri, Minas Ithil/Minas Morgul, Fornost Erain/Fornost, Colle Vento/Amon Sûl, Tumulilande/Tyrn Gorthad, Brandivino/Baranduin, Azanulbizar/Nanduhirion, Terre Selvagge/Rhovanion). Il modello dei dati è spiegato in `data/MODELLO.md`.
- **Eventi collegati ai luoghi (novembre 2026)**: tutti i **175 riferimenti** di luogo nelle schede evento ora usano gli ID (`luoghi: [minas-tirith, ...]`), non più i nomi; i doppioni nati dagli alias sono stati unificati. Il build verifica che ogni ID esista e produce `place`/`places` con i nomi per la visualizzazione, `place_ids` con gli ID per le relazioni, la tabella SQL `places (event_id, place_id, name)` e gli indici `per_luogo` e `per_luogo_id`. Il sito continua a mostrare i nomi: 61 eventi, nessun errore in console.
- **Anagrafica dei partecipanti (novembre 2026)**: `data/persone.yaml` contiene **90 personaggi** e `data/entita.yaml` contiene **43 entità collettive** (popoli, regni, gruppi). Insieme coprono **tutti i 133 nomi** di partecipante citati dagli eventi. Il build valida ID, alias, specie, date e nomi duplicati tra i due file, e produce `build/persone.json`, `build/entita.json`, `build/rapporto-persone.md`, `build/rapporto-entita.md` e `build/rapporto-partecipanti.md`. Anche i **296 riferimenti** nei partecipanti degli eventi ora usano gli ID (`persona:` o `entita:`), non più i nomi; il build risolve i nomi per la visualizzazione e conserva `id` e `tipo` in `js/data.js`.
- **Base del database completata (novembre 2026)**: eventi, luoghi e partecipanti sono collegati per ID e validati. Per la vetrina e la mappa i dati necessari ci sono.
- **Espansione dell'Appendice B, scelta B (novembre 2026)**: dopo i primi 61 eventi, il lavoro continua per coprire tutti gli anni dell'Appendice B. Blocchi annuali completati: **204 eventi**, **119 anni su 127** coperti. La cronologia annuale dell'Appendice B è completa: gli 8 anni rimasti sono già raccontati dentro eventi-intervallo (Isildur 2-3, Carrieri 1851-1856, Balrog 1980-1981, Eärnur 2043-2050, Draghi 2589-2590, Gandalf a Dol Guldur 2841-2850) o sono la semplice annotazione di un regno (1149). Dei Grandi Anni 3018-3019 sono coperti i passaggi principali, dal viaggio di Frodo alla battaglia della Valle, alla distruzione di Dol Guldur, a Cormallen, alle nozze e al ritorno nella Contea; restano da rifinire le giornate minori e alcuni dettagli del 3020-3021. I nuovi eventi usano gli stessi ID di luoghi e partecipanti; il frontend resta invariato.
- **Controllo del database (novembre 2026)**: aggiunto `build/rapporto-dati.md`, generato dal build. Alla data attuale: 204 eventi, 100 luoghi, 119 personaggi, 51 entità, 582 partecipanti e 403 citazioni di luogo; **0 partecipanti senza scheda, 0 luoghi senza scheda, 0 schede senza eventi**. Le parti dei partecipanti sono state normalizzate (Imladris → Gran Burrone, Dúnedain → Dúnedain del Nord, popolo del Nord → Éothéod) e i ruoli con maiuscole incoerenti sono stati uniformati. Restano 48 parti, 163 ruoli e 415 esiti: sono testi descrittivi, non codici; le parti generiche (Nord, Est, Montagne, invasori, ribelli) sono dichiarate come tali. Se serviranno filtri per ruolo/esito, andrà aggiunto un vocabolario controllato separato.
- **Parentele, pilota Casa di Elrond (novembre 2026)**: creato `data/relazioni.yaml` come file di **archi** separato dalle persone: 11 relazioni (8 genitore, 3 coniuge) che collegano 8 persone. Aggiunto il campo `genere: m/f` alle persone coinvolte. Il build valida ID, generi, duplicati, cicli, doppio padre/madre e ordine delle nascite, e produce `build/relazioni.json`, `build/rapporto-parentele.md` e `build/alberi.md` (albero testuale). I fratelli sono derivati dai genitori comuni; i coniugi si scrivono una volta sola. Il frontend resta invariato: prima si valida il modello, poi si disegna.
- **Parentele, Casa di Isildur (novembre 2026)**: aggiunte **31 persone** e **46 archi**, per un totale di **150 personaggi** e **57 relazioni** (52 genitore, 5 coniuge) che collegano 52 persone in un unico gruppo familiare. La linea settentrionale va da Elendil a Aragorn II: 8 Alti Re dell'Arnor, 15 re dell'Arthedain, 15 Capitani dei Dúnedain del Nord, più Anárion e Meneldil per la diramazione meridionale. Anni di morte presi dalla tavola dell'Appendice A. Correzioni dichiarate: **Amlalth → Amlaith**, **Argevil → Arvegil** (il testo narrativo usa Arvegil), **Argeleb I †356 → 1356** (confermato dall'Appendice B). Aggiunti i matrimoni Arvedui ⚭ Firiel e Arathorn II ⚭ Gilraen, e le madri Firiel e Gilraen. Il `rapporto-dati.md` ora distingue i personaggi senza eventi ma collegati da parentela (31) da quelli davvero isolati (0). L'albero testuale segnala con «(già mostrato sopra)» i matrimoni che uniscono due casate, perché un albero non può ripetere due volte lo stesso nodo.
- **Parentele, Sovrintendenti e Hobbit (novembre 2026)**: aggiunta la Casa di Húrin (i Sovrintendenti di Gondor: 23 schede nuove e 11 corrette, 35 relazioni, con la casa di Dol Amroth e il matrimonio Éowyn ⚭ Faramir) e le quattro tavole hobbit dell'Appendice C (Baggins, Tuc, Brandibuck, Gamgi: 108 schede nuove, 120 relazioni). Le date hobbit sono state convertite dal Calendario della Contea alla Terza Era (anno + 1600). Nomi dichiarati in `glossario.md`: Eradan (l'epub scrive «Elladan»), Húrin/Túrin con l'accento acuto (l'epub usa il grave), Boromir I, Beregond I, Hamfast Gamgi II (numerazione del sito). Restano fuori i rami collaterali delle tavole hobbit e la linea meridionale di Anárion.
- **Ordine delle fasi rivisto (novembre 2026)**: la timeline v1 è considerata chiusa a 204 eventi. Ordine concordato: **parentele** (pilota Casa di Elrond, poi Isildur, Rohan, Durin, Sovrintendenti, Hobbit) → **progetto mappa** (proiezione, scala, stile, base disegnata da zero) → **coordinate dei luoghi** → **vocabolario controllato** di ruoli ed esiti → **vetrina**. Le coordinate vengono dopo la mappa perché dipendono dalle decisioni grafiche; le parentele no.
- **Bozza della vetrina (novembre 2026)**: creata `schede.html` come prova di elenco delle 61 schede, con ricerca e dettagli. Il primo tentativo non era integrato con il cerchio (il link si sovrapponeva alla nota) e la pagina è stata tolta dalla pubblicazione: resta in repository come bozza, da riprendere dopo il completamento del database.
- **Decisioni d'impianto (Blocco 0)**: hosting GitHub + Pages, dominio gratuito per ora, una sola pagina in v1 (generatore statico solo se si supereranno 6–8 pagine o servirà la SEO per singolo evento), statico senza build, font da auto-ospitare nel repository, divisione del lavoro: OpenCode scrive codice e bozze di contenuti, l'utente corregge e decide le convenzioni. Il piano completo è in `~/.opencode/plan/piano-cronologia-arda.md` (fuori dal repo).
- **Tipo evento** (vocabolario attuale, validato dal build): fondazione, battaglia, guerra, distruzione, perdita, tradimento, morte, nascita, viaggio, consiglio, politica, evento. `place`, `people`, `places`, `participants`, `sources` sono ora popolati; `people` è la lista piatta dei nomi usata dal cerchio, `participants` la tabella strutturata con parte, ruolo ed esito.
- **Piano concordato in 5 fasi**: 0 impianto → 1 dataset Terza Era (45–55 eventi da Appendice B) → 2 mappa Terza Era ad alto dettaglio → 3 funzioni (zoom, ricerca, filtri, mappa a schermo intero; pannello laterale solo, in v1) → 4 apertura altre Ere → 5 alberi genealogici da Appendice A.
- Problema noto nel cerchio: gli eventi del 3018–3021 si addensano in fondo al cerchio; lo zoom (fase 3) è la soluzione, per ora sono solo distanziati.

## 10. Punto di ripartenza (da aggiornare a fine sessione)

Le sezioni precedenti raccontano la storia del progetto. Questa dice dove siamo **adesso**: è la memoria breve da cui ripartire in una sessione nuova.

### Stato attuale

- **Timeline v1 chiusa**: 204 eventi della Terza Era, 100 luoghi, 320 personaggi, 51 entità, 582 partecipanti, 403 citazioni di luogo; 0 schede mancanti.
- **Parentele**: modello ad archi in `data/relazioni.yaml`, validato dal build (ID, generi, duplicati, cicli, doppio padre/madre, ordine delle nascite). Sono completi sei gruppi: Casa di Elrond (11 relazioni), Casa di Isildur (46, da Elendil ad Aragorn II), Casa di Eorl (38, da Léod a Elfwine), Casa di Durin (30, da Durin I a Durin VII), Casa di Húrin (35: i Sovrintendenti di Gondor da Húrin di Emyn Arnen a Faramir, con la casa di Dol Amroth e il matrimonio Éowyn ⚭ Faramir) e gli Hobbit (120: Baggins, Tuc, Brandibuck, Gamgi, da Gorhendad a Samvise e ai suoi tredici figli; 117 persone collegate). Totale: **280 archi** (241 genitore, 39 coniuge) e **268 persone collegate** in 4 gruppi familiari. Le date hobbit sono convertite dal Calendario della Contea alla Terza Era; i nomi ambigui sono dichiarati in `glossario.md`.
- **Mappa (novembre 2026)**: cantiere aperto, con una svolta: la sagoma la **disegna l'utente a mano** in Procreate. Specifiche in `mappe/tavola/README.md`; base da importare in `mappe/tavola/base-3560x3760.png` (3560 × 3760 px, 2 px = 1 miglio, cornice x −560…1220, y −700…1180). Livelli richiesti: costa, isole, laghi (priorità), poi rilievo, foreste, paludi, deserti, fiumi. La traccia automatica per zone è ferma: `mappe/terza-era/costa/01-forochel.js` (86 punti) resta solo come prova. Al ritorno del disegno: sostituire `mare.js`, riposizionare i luoghi, poi rilievo, fiumi, vegetazione, etichette; il banco di prova resta `mappe/terza-era.html`. Regola fissata: la mappa non si converte con una scala unica (la carta è deformata), quindi ogni elemento si controlla contro i luoghi.
- **Vetrina**: `schede.html` resta una bozza non pubblicata, da riprendere dopo il completamento del database.
- **Repository ripulito (novembre 2026)**: cancellati `prototipi/cerchio-a-inchiostro.html` e `prototipi/cerchio-con-mappa.html`, ormai superati dal sito vero, insieme alla bozza non tracciata `bozze/prova-warp.html`. Il codice da guardare è `index.html` con `js/`.
- **Regole di lavoro aggiornate (novembre 2026)**: in `AGENTS.md` chiarito che si usano prima gli strumenti di lettura e ricerca e solo dopo la shell (un comando mirato invece di molti piccoli), e aggiunta la regola «una sessione = un lavoro»: sessione nuova a lavoro chiuso, stop dopo due compattazioni, modello fisso per sessione.

### Prossimi passi (in ordine)

1. Mappa: **in attesa della tavola disegnata a mano** (sagoma: costa, isole, laghi). All'arrivo: portarla in miglia, riposizionare i luoghi, sostituire `mare.js`.
2. Mappa, a seguire: rilievo, fiumi, vegetazione, etichette; prove sul telefono e inserimento nel sito.
5. Dopo la mappa: vocabolario controllato di ruoli ed esiti, infine la vetrina.
6. Parentele: restano solo la linea meridionale di Anárion e i rami collaterali hobbit (Boffin, Bolgeri, Cotton, Rintanati), da fare solo se serviranno.

### Decisioni da non dimenticare

- **Se l'epub Bompiani 2004 dice X, il sito dice X.** I nomi ufficiali vivono in `glossario.md`.
- **Costa e luoghi nello stesso spazio**: la deformazione che ha prodotto `luoghi.js` (TPS in `tools/estrai-mappa.py`) è la base comune delle zone. La carta di riferimento è deformata: non esiste una scala unica (errore medio 168 miglia), quindi non si converte con una semplice proporzione.
- **Omonimie dei Nani**: i re della linea di Durin sono «Glóin I» e «Óin I» (numerazione del sito), i compagni di Thorin restano «Glóin» e «Óin».
- Mappe disegnate da zero, mai copiate da mappe ufficiali (comprese quelle di Christopher Tolkien).
- La mappa si ridisegna a mano guardando la carta di mapmiddleearth.com (CC BY-NC 4.0): la carta non si pubblica, il credito resta obbligatorio e il sito non si vende.
- Sito statico, solo frontend, hosting GitHub Pages. Tutto in italiano, sito fan non commerciale.
- La timeline v1 è chiusa: nuovi eventi solo su richiesta esplicita dell'utente.
- I file in `data/` sono l'unica fonte dei dati; `build/` e `js/data.js` sono generati da `tools/build_data.py`.

### Come si aggiorna questa sezione (per l'utente)

- A fine lavoro cambia solo le righe di **Stato attuale** e **Prossimi passi**.
- Se prendi una decisione importante, aggiungila alle **Decisioni da non dimenticare**.
- Non serve riscrivere le altre sezioni: restano come storia del progetto.
