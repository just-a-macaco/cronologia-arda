# Mappa — appunti di cantiere

Note per la sessione che riprende il lavoro. Non è documentazione del sito: è la lavagna.

## Decisione presa (novembre 2026)

Strada **B**: la mappa si **ridisegna a mano** guardando la carta di riferimento.
La carta **non** si usa come sfondo né si pubblica nel repository.

## Il riferimento

- URL: `https://mapmiddleearth.com/crops/en/full.webp` (1800 × 1200, orizzontale)
- Licenza: CC BY-NC 4.0 (non commerciale, credito). Il sito è fan e senza
  pubblicità, quindi è compatibile.
- Non è nel repository: va riscaricato a ogni sessione (o tenuto fuori dal repo,
  in una cartella temporanea).
- Attenzione: la carta è **orizzontale**, copre dal Forochel al Rhûn e scende
  fino all'Harad. Le proporzioni della nostra mappa devono seguire lei.

## Perché la mappa attuale non va

- La costa in `mappe/terza-era/mare.js` viene da `bozze/costa.json`: 278 punti
  per ~3000 miglia. È una semplificazione della semplificazione.
- Il confronto con il riferimento: la linea combacia con quella bozza (scarto
  medio 4 miglia), ma la bozza non ha le insenature vere (baie, capi, foci,
  isolotti). Da qui l'effetto «blob».
- Il rilievo attuale è una fascia con una fila di triangoli: sembra una cerniera.
- Il Mare di Rhûn è un sasso tondo.

## Come si ridisegna (metodo)

1. Aprire il riferimento e ridurlo a una griglia di miglia (200 miglia).
2. Zona per zona, tracciare i punti della costa leggendo la carta: un punto ogni
   8–10 miglia sui tratti dritti, molto più fitto dentro baie e capi.
3. Dopo ogni zona, renderizzare solo quella zona con lo zoom e confrontarla con
   la carta: se non combacia, correggere prima di passare avanti.
4. Solo alla fine, attaccare le zone in un'unica costa.

## Zone da rifare (in ordine)

- [ ] Forochel e la costa nord (baia, capi, ghiacci)
- [ ] Lindon e il Golfo di Lune (fiordo stretto, Porti Grigi in fondo)
- [ ] Harlindon e Minhiriath (Eryn Vorn, foce del Brandivino)
- [ ] Enedwaith e Andrast (capo lungo, foce dell'Isen)
- [ ] Baia di Belfalas (Dol Amroth, Linhir, Pelargir)
- [ ] Delta dell'Anduin e Tolfalas (ventaglio di foci)
- [ ] Harondor e Umbar (baia, promontorio)
- [ ] Costa di Harad
- [ ] Mare di Rhûn e Núrnen
- [ ] Isole: Himling, Tol Fuin, Tol Morwen

## Rilievo

- Le catene sono **fasce dense** di cime piccole, non una linea a zig-zag.
- Riferimento: Monti Nebbiosi, Ered Luin, Monti Grigi, Monti Bianchi, Ephel Dúath,
  Ered Lithui, Angmar, Ettenmoors.
- Le cime vanno disegnate a file sfalsate, con altezze irregolari.

## Cosa c'è già nel codice

- `mappe/terza-era.html` — pagina di prova, stile «Atlante», griglia ogni 200 miglia.
- `mappe/terza-era/dati.js` — rilievo, fiumi, boschi, nomi (nostri).
- `mappe/terza-era/mare.js` — costa e acque (da rifare, viene dalla bozza).
- `mappe/terza-era/luoghi.js` — 106 luoghi con nome e coordinate (base mapmiddleearth).
- `mappe/terza-era.html` disegna tutto: si può tenere come banco di prova.

## Trappole già incontrate

- `bozze/mappa-dati.json` contiene un poligono del **mare** con tagli diagonali:
  non usarlo per riempire la terra (riempie zone sbagliate).
- `bozze/costa.json` è la costa semplificata: va bene solo come confronto.
- Il poligono del mare ha segmenti lunghi (i tagli): non vanno tracciati come costa.
- La pagina fallisce in silenzio se un blocco JS va in errore: controllare la console.

## Criterio di chiusura della mappa

- Si legge nel cerchio piccolo e a schermo intero sul telefono.
- Costa e rilievo somigliano alla carta di riferimento, non a un blob.
- Tutti i 100 luoghi sono al posto giusto.
- Credito a mapmiddleearth.com visibile.
