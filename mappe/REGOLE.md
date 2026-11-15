# Regole della mappa della Terza Era

Decisioni prese a novembre 2026. Valgono per tutte le sessioni che lavorano sulla mappa.
Se una regola va cambiata, si cambia qui e si annota in `PROJECT.md`, non a voce.

## Area

- Dal Lindon (Ered Luin) a est fino al Mare di Rhûn e a Mordor.
- Da nord: Forochel e i Monti del Ghiaccio. Da sud: la Baia di Belfalas, con un
  margine di Harad e di Umbar.
- Cornice quasi quadrata: la mappa sta al centro del cerchio, che è quadrato.
- Fuori area: Valinor, Númenor, le terre a est di Rhûn.

## Scala

- Una sola: **1 unità = 1 miglio**. Le distanze fra i luoghi sono quelle dei libri.
- Griglia di riferimento ogni 200 miglia, solo per il lavoro (non si pubblica).
- La mappa è un atlante, non un rilievo: le forme sono semplificate, le distanze no.

## Stile

- Palette «Atlante» del sito: fondo `#f2f3f4`, inchiostro `#1a1d21`, grigio `#6b7178`,
  linee `#d7dbde`, un solo accento rosso mattone `#b23a2e`.
- Acqua: riempimento chiarissimo, costa a tratto sottile. Niente sfumature, niente
  texture, niente pergamena.
- Montagne: catene disegnate una per una, a trattini; non un mucchio di picchi.
- Foreste: gruppetti di alberelli stilizzati. Paludi: trattini orizzontali.
- L'accento rosso si usa solo per una cosa alla volta (il luogo dell'evento scelto).

## Cosa c'è e cosa non c'è

- C'è: coste, isole, laghi, fiumi, montagne, colline, foreste, paludi, deserti,
  città e luoghi del database, nomi delle regioni.
- Non c'è: confini politici (cambiano con le ere), strade (nemmeno le grandi),
  simboli decorativi, mostri, stemmi.

## Nomi

- Italiani, presi da `glossario.md`. Se l'epub Bompiani 2004 dice X, la mappa dice X.
- Tre livelli: regioni in maiuscoletto spaziato, città in tondo, fiumi e mari in
  corsivo, più piccoli e grigi. Rispettare la gerarchia: la Contea non è scritta
  come il Mare di Rhûn.

## Leggibilità

- Due livelli di dettaglio: nel cerchio (piccolo) solo i nomi principali; a schermo
  intero tutti i luoghi. Ogni nome deve restare leggibile a 360 px di larghezza.
- I nomi non si sovrappongono mai ai simboli né fra loro: se due luoghi sono vicini,
  si sposta l'etichetta, non il luogo.

## Provenienza

- La **costa e le acque** sono adattate dalla carta di **mapmiddleearth.com**
  (licenza CC BY-NC 4.0: uso non commerciale, credito obbligatorio). Il credito
  va scritto nella pagina della mappa e nel sito: «Costa e acque adattate da
  mapmiddleearth.com (CC BY-NC 4.0)».
- Il resto è nostro: rilievo, fiumi, boschi, etichette, stile, impaginazione.
- Resta vietato copiare le mappe ufficiali (Tolkien, Christopher Tolkien,
  edizioni Bompiani e simili).
- La mappa non si vende e il sito non ha pubblicità: la licenza lo permette solo
  a queste condizioni.
- Se un giorno si togliesse il credito o si mettesse in vendita qualcosa, la
  base va rifatta da zero.

## Come è fatta la mappa (tecnica, in breve)

- Un file `mappe/terza-era.svg` con i livelli separati: acqua, coste, rilievo,
  vegetazione, fiumi, luoghi, etichette.
- Le coordinate dei luoghi stanno in `data/luoghi.yaml`; la geometria della mappa
  in `mappe/terza-era/*.json`, generata o corretta a mano, mai da fonti esterne.
- Il sito legge la mappa dal file: nessuna modifica a `index.html` finché la mappa
  non è approvata.
