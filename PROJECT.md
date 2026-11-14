# Cronologia di Arda: documento di passaggio

Sito fan non commerciale su Tolkien (Il Signore degli Anelli, Lo Hobbit, Il Silmarillion e altri scritti). Lingua del sito e dei testi: **italiano**.

Questo file riassume obiettivi, decisioni prese, stato del codice e prossimi passi. Il codice esistente è in `prototipi/`. Leggi prima tutto il file, poi apri `prototipi/cerchio-con-mappa.html`.

## 1. Obiettivo: tre funzioni

1. **Timeline completa** di tutta la storia raccontata da Tolkien, non solo il Signore degli Anelli: tutte le Ere (Lampade, Alberi, Prima, Seconda, Terza, e in prospettiva Quarta).
2. **Alberi genealogici** di tutti i personaggi principali.
3. **Mappe interattive** della Terra di Mezzo, di Númenor e di Valinor. Interattive significa che mostrano dove si sono svolti eventi e battaglie e come la geografia cambia nel tempo.

Si parte dalla timeline. Le altre due funzioni vanno progettate in modo che condividano i dati con la timeline.

## 2. Decisioni già prese dall'utente

- **Interfaccia timeline:** cerchio con gli anni e le note intorno, ispirato all'infografica "Timeline of the One Ring" di lotrproject.com (Emil Johansson). Il cerchio è la linea del tempo, la mappa sta **al centro del cerchio**, e dall'evento sull'anello parte una linea fino al luogo sulla mappa.
- **Variante grafica scelta:** "infografica" (file `cerchio-a-infografica` nella storia del progetto; il prototipo attuale ne deriva). Alternativa non scelta ma non bocciata: "inchiostro", in `prototipi/cerchio-a-inchiostro.html`.
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

## 4. Stato del codice (`prototipi/cerchio-con-mappa.html`)

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
- **Fase 0 completata**: progetto strutturato (git attivo). `index.html` + `css/main.css` + `js/circle.js` (disegno del cerchio) + `js/data.js` (dataset). **Nota tecnica**: i dati sono in file `.js` con costanti globali e non JSON puro, per far funzionare la pagina anche aprendola direttamente da file senza server. Se in futuro si passa a fetch+JSON serve un server locale. Nessun build.
- **Fonti**: in `fonti/` (ignorata da git, testi protetti) ci sono LoTR con Appendici (Bompiani 2004) e Lo Hobbit in .epub. Estrazione del testo dell'Appendice B in `fonti/estrazione/`. Serve anche Il Silmarillion per la fase 4.
- **Git non ancora attivo**: mancano gli Xcode Command Line Tools (installazione avviata al primo `git init`; riprendere con `git init` e primo commit quando disponibili).
- **Piano concordato in 5 fasi**: 0 impianto → 1 dataset Terza Era (45–55 eventi da Appendice B) → 2 mappa Terza Era ad alto dettaglio → 3 funzioni (zoom, ricerca, filtri, mappa a schermo intero; pannello laterale solo, in v1) → 4 apertura altre Ere → 5 alberi genealogici da Appendice A.
- Problema noto nei prototipi: gli eventi del 3018–3021 si addensano in fondo al cerchio; lo zoom (fase 3) è la soluzione, per ora sono solo distanziati.
