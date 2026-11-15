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
- `proposte/`, `bozze/` — materiale storico o in attesa: consultare solo se richiesto.

## Regole di lettura (il contesto è di 200.000 token: si esaurisce in fretta)

- Prima lo strumento giusto, poi la shell. Per leggere un file: strumento di lettura con
  `offset`/`limit`. Per cercare: `grep`. La shell serve per lanciare script, non per
  leggere o cercare.
- Un comando solo e mirato, non cinque comandi piccoli. Se un output supera le 40 righe,
  filtrare (`grep`, `-m`, `head`) o salvare su file e riportare solo il riepilogo.
- Mai `cat` di file interi. Mai leggere per intero file oltre ~20 KB, e mai
  `fonti/**`, `build/**`, `js/data.js`, `fonti/estrazione/mme/*` (l'SVG è 1,8 MB),
  `.epub`, `.sqlite`, immagini.
- Cercare in questo ordine: `rg -l "testo"` (quali file) → `rg -c` (quante volte) →
  `rg -n -m 10` (massimo 10 righe). Solo dopo leggere il pezzo che serve con `read` e
  `offset`/`limit`.
- Non rileggere un file già letto nella stessa sessione: se il dato serve ancora, usa
  quello che hai già visto o rileggi solo poche righe intorno.
- Non scaricare pagine web intere: se serve un dato da una pagina, estrarre solo quella parte.
- Non incollare testi lunghi in chat: basta il nome del file e la sezione da guardare.
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
- A fine lavoro, sempre: aggiornare la sezione 10 di `PROJECT.md`, poi `git add`, `git commit`
  e `git push` su GitHub. Non chiedere conferma per il push: l'utente lo vuole sempre, per non
  perdere lavoro. Chiedere conferma solo se il push pubblicherebbe qualcosa di protetto
  (testi o mappe delle fonti) o se `fonti/` comparisse tra i file da caricare.
- Se il push fallisce (rete, chiave SSH), dirlo subito e lasciare il commit fatto in locale.

## Una sessione = un lavoro

- Una sessione per un lavoro, non una sessione per tutta la giornata. Quando il lavoro è
  chiuso (commit e push fatti), dirlo chiaramente e aprire una sessione nuova.
- Se la sessione si compatta due volte, fermarsi subito: aggiornare la sezione 10 di
  `PROJECT.md` con lo stato raggiunto e ripartire in una sessione nuova leggendo solo
  quella sezione.
- Non cambiare modello a metà sessione: obbliga a rileggere tutto da capo.
