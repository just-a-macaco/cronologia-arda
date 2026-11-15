# Tavola per la mappa disegnata a mano

Istruzioni per chi disegna (Procreate). Il file `base-3560x3760.png` è la base da
importare: griglia, cornice e 106 luoghi provvisori.

## Tavola

- **3560 × 3760 px**, sRGB, sfondo **trasparente**, 132 dpi (il dpi non conta).
- **2 px = 1 miglio.** La tavola corrisponde esatta alla cornice della mappa:
  - x da −560 a 1220 miglia, y da −700 a 1180 miglia;
  - miglia_x = px_x / 2 − 560;  miglia_y = px_y / 2 − 700.
- Nord in alto, nessuna rotazione, nessun margine interno.
- Se Procreate fatica con i livelli: 2670 × 2820 px (1,5 px per miglio), stessa
  cornice. Dirlo prima di iniziare.
- La costa può uscire dai bordi: non serve chiuderla, la chiudo io lungo la cornice.

## Livelli (nomi esatti, dal fondo alla cima)

| Livello | Cosa | Tratto |
|---|---|---|
| `00-riferimento` | la base importata (griglia + puntini) | non è disegno, si nasconde all'esportazione |
| `10-costa` | linea di costa, continua | 8 px |
| `11-isole` | contorni chiusi | 6 px |
| `12-laghi` | contorni chiusi (Evendim, Rhûn, Núrnen…) | 5 px |
| `13-fiumi` | una linea per fiume, dalla sorgente alla foce | 4 px |
| `14-rilievo` | catene di montagne, cime piccole in fila | 5 px |
| `15-colline` | colline e alture | 4 px |
| `16-foreste` | contorno leggero + alberelli stilizzati | 4 px |
| `17-paludi` | trattini orizzontali | 3 px |
| `18-deserti` | trattini o puntini radi | 3 px |
| `99-schizzo` | costruzioni, da non usare | — |

## Regole del disegno

- Solo inchiostro: nero `#1A1D21`, opacità 100%. **Niente riempimenti, ombre,
  colori, texture, pergamena.** I riempimenti li mette il sito.
- Niente nomi né scritte: le etichette le mette il sito dal database.
- Niente tratto calligrafico che si assottiglia da solo: spessore costante.
- I puntini rossi della base sono i luoghi attuali, ma vengono da una base
  deformata: **non forzare la geografia per farli combaciare**. Disegna la
  geografia giusta; i luoghi li riposiziono io dopo.
- Non ricalcare mappe protette (Tolkien, Christopher Tolkien, Bompiani). La carta
  di mapmiddleearth si può guardare, il disegno deve essere nostro.

## Cosa consegnare

1. **Priorità: la sagoma** — `10-costa`, `11-isole`, `12-laghi`. Con questa la
   mappa riparte.
2. Poi, quando vuoi: rilievo; poi foreste, paludi, deserti; poi fiumi.
3. Formato: **PSD** con i livelli nominati come sopra (Procreate: Condividi →
   PSD) + un **PNG appiattito con sfondo trasparente** per il controllo veloce.
   Se il PSD non arriva bene: un PNG per livello, stesso nome
   (`10-costa.png`, `11-isole.png`, …), stessa dimensione della tavola.
4. Il file `.procreate` tienilo tu: serve per le correzioni, non entra nel repo.

## Cosa faccio io quando arriva

- Ritaglio/raddrizzo se serve e porto la sagoma in miglia (stessa cornice).
- Riga per riga: controllo che i luoghi cadano sulla terra e non in mare.
- Sostituisco `mappe/terza-era/mare.js` con la costa nuova, poi rilievo, fiumi,
  vegetazione, etichette. Il banco di prova resta `mappe/terza-era.html`.
