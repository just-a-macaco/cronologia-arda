# Regole di lavoro su Cronologia di Arda

Valgono per ogni sessione. Il progetto è in questa cartella.

## Mappa del progetto

- `data/` — i dati veri: `eventi/*.yaml`, `persone.yaml`, `luoghi.yaml`, `entita.yaml`,
  `relazioni.yaml`. Il modello è spiegato in `data/MODELLO.md`. **Si modificano solo qui.**
- `tools/` — script Python. `build_data.py` valida i dati e genera tutto il resto.
- `build/` — tutto generato da `tools/build_data.py` (`arda.sqlite`, `indexes.json`,
  `schede-terza-era.md`, `rapporto*.md`, `alberi.md`, JSON vari).
  **Non leggerlo a mano, non modificarlo a mano.**
- `fonti/` — libri originali (epub) e testo estratto (`appendice-b.txt`, `mme/`).
  Testi protetti, non pubblicati. **Non leggerli interi.**
- `js/`, `css/`, `*.html` — il sito. `js/data.js` è generato: non modificarlo a mano.
- `PROJECT.md` — stato, decisioni, prossimi passi. `glossario.md` — nomi ufficiali.
- `proposte/`, `prototipi/`, `bozze/` — materiale storico o in attesa: consultare solo se richiesto.

## Regole di lettura (il contesto è di 200.000 token: si esaurisce in fretta)

- Massimo 40 righe di output per comando. Oltre, filtrare o salvare su file e riportare solo il riepilogo.
- Mai `cat` di file interi. Mai leggere per intero file oltre ~20 KB, e mai
  `fonti/**`, `build/**`, `js/data.js`, `fonti/estrazione/mme/*` (l'SVG è 1,8 MB),
  `.epub`, `.sqlite`, immagini.
- Cercare in questo ordine: `rg -l "testo"` (quali file) → `rg -c` (quante volte) →
  `rg -n -m 10` (massimo 10 righe). Solo dopo leggere il pezzo che serve con
  `sed -n 'inizio,finep'` o con `read` e `offset`/`limit`.
- Non scaricare pagine web intere: se serve un dato da una pagina, estrarre solo quella parte.
- Per i JSON grandi usare `jq` su un singolo campo, non aprire il file.
- Non incollare output lunghi nei messaggi: riassumere.

## Dati

- I file in `data/` non si scrivono a mano dalla chat: si modifica lo script (o si fanno
  modifiche piccole e mirate) e si lancia `python3 tools/build_data.py`.
- Dopo ogni build mostrare solo: quanti eventi, luoghi, persone; eventuali errori; un esempio.
  Il resto è già in `build/rapporto*.md`.
- Mai toccare a mano `build/` e `js/data.js`: sono generati.
- Regola dei nomi, senza eccezioni: **se l'epub Bompiani 2004 dice X, il sito dice X.**
  I nomi nuovi vanno aggiunti a `glossario.md`, non sparsi nei testi.
- Prima di aggiungere eventi, luoghi o persone: controllare che non esistano già
  (per ID e per alias).

## Come lavorare con l'utente

- Italiano semplice, niente gergo. Prima il risultato, poi al massimo una frase di spiegazione.
- L'utente non è programmatore: ogni passaggio tecnico va spiegato in una riga, a cosa serve.
- Prima di un lavoro lungo: piano in 5 righe, poi esecuzione.
- Niente complimenti né adulazione; essere critici quando serve.
- A fine lavoro, aggiornare la sezione 10 di `PROJECT.md` (stato attuale, prossimi passi).
