# Il modello dei dati, spiegato semplice

Questo file non è codice: è la mappa di come sarà organizzato il "database" del sito.
Serve a noi due per non perderci quando i dati crescono.

## 1. Il principio: il database è dentro il progetto

Non c'è un server con un database acceso. Non serve.

Il database è fatto di **file di testo** dentro la cartella `data/`, salvati in Git.
Git è la macchina del tempo: ogni modifica resta registrata, si può annullare, si può
confrontare. Il sito viene costruito leggendo quei file.

Questo è lo stesso sistema usato da mapmiddleearth.com: quel sito non interroga un
database, ha un file JSON con 156 luoghi, 380 eventi e 9 viaggi, preparato prima.
Noi faremo la stessa cosa, ma con i file separati e leggibili.

## 2. Le cinque scatole

Tutto ciò che raccontiamo sta in una di queste cinque scatole.

| Scatola | Cosa contiene | Esempio |
|---|---|---|
| **Eventi** | cose che accadono in un momento | la Battaglia dei Campi del Pelennor |
| **Persone** | chi agisce | Frodo Baggins, Gandalf, Théoden |
| **Luoghi** | dove accade | la Contea, Minas Tirith, Mordor |
| **Famiglie** | legami di parentela | la casa di Elrond, i Re del Mark |
| **Fonti** | da dove sappiamo una cosa | Appendice B, libro V capitolo 6 |

Le famiglie non hanno una scheda propria: sono **archi** in
`data/relazioni.yaml`, perché una parentela riguarda sempre due persone.

Un evento non "contiene" le persone: le **richiama** tramite un codice.
È la differenza tra un tema scolastico e un database.

## 3. Il codice univoco (ID)

Ogni cosa ha un codice breve, minuscolo, senza spazi, che non cambia mai.

```
frodo-baggins
gandalf
contea
minas-tirith
pelennor
```

Regole:

- l'ID non si traduce e non si corregge: è come il codice fiscale;
- il nome visibile sì, può cambiare quante volte vogliamo;
- se sbagliamo un nome, lo cambiamo in un punto solo e cambia ovunque.

Esempio: oggi in 9 schede compare "Aragorn". Domani decidiamo che il nome visibile
è "Aragorn figlio di Arathorn". Cambiamo una riga nella scheda di Aragorn; le 9
schede si aggiornano da sole.

## 4. Come si collegano

### Una persona

```yaml
# data/persone.yaml
id: frodo-baggins
nome: Frodo Baggins
tipo: personaggio
popolo: Hobbit
genere: m
nascita: 2968
morte: null
alias:
  - Frodo
```

`nascita` e `morte` sono anni della **Terza Era**. Per le altre Ere l'anno si
scrive nella `nota` (per esempio Elendil, morto nel S.E. 3441), così non si
confondono due calendari nello stesso campo.

### Un luogo

```yaml
# data/luoghi.yaml
id: contea
nome: la Contea
tipo: regione
alias:
  - Shire
```

### Un evento che li richiama

```yaml
# data/eventi/...yaml
id: distruzione-anello
titolo: Distruzione dell'Anello
luoghi:
  - monte-fato
  - sammath-naur
partecipanti:
  - persona: frodo-baggins
    ruolo: Portatore
    esito: cede all'Anello, poi viene salvato
  - persona: samvise-gamgi
    ruolo: compagno
    esito: sopravvive
```

Il computer, in fase di costruzione, controlla che `frodo-baggins` e `monte-fato`
esistano davvero. Se mancano, il sito non si costruisce e ci dice il motivo.
Meglio un errore sul computer che una scheda sbagliata online.

### Una parentela

Le parentele non stanno dentro la scheda della persona. Stanno in un file
separato, `data/relazioni.yaml`, fatto di **archi**: una riga collega due
persone.

```yaml
# data/relazioni.yaml
- da: elrond
  a: arwen
  tipo: genitore
  certezza: certa
  fonti:
    - opera: Il Signore degli Anelli
      riferimento: "Appendice A, La storia di Aragorn e Arwen"
```

Regole:

- `genitore`: `da` è il genitore, `a` è il figlio.
- `coniuge`: si scrive **una volta sola**; il computer la legge in entrambe le
  direzioni.
- I **fratelli non si scrivono**: si ricavano dai genitori comuni.
- Ogni persona citata in una relazione deve avere `genere: m` o `genere: f`,
  perché senza genere non si distingue un padre da una madre.
- Se una persona ha più coniugi, per ora il disegno la raggruppa in un solo
  nodo. Quando servirà, i matrimoni avranno un identificativo proprio.
- `certezza: certa` quando il testo dice il legame; `certezza: probabile` quando
  il legame si ricava solo dalla successione, come nella lista dei re del Mark.

Il computer controlla che gli ID esistano, che nessuno sia genitore di se
stesso, che non ci siano cicli, che un figlio non abbia due padri o due madri,
e che un genitore non sia nato dopo il figlio.

## 5. La distinzione più importante: persona non significa "nome nella tabella"

Oggi nella colonna "partecipanti" erano finiti anche regni e popoli:

- Gondor
- Rohan
- Arthedain
- gli Orchetti
- i Nazgûl

Non sono personaggi. Sono **entità** di tipo diverso. Se li teniamo tutti come
"persone", gli alberi genealogici e le pagine dei personaggi diventano un disastro.

Quindi ogni scheda ha un `tipo`:

| Tipo | Esempi |
|---|---|
| `personaggio` | Frodo, Galadriel, Théoden |
| `popolo` | Hobbit, Nani, Rohirrim |
| `regno` | Gondor, Rohan, Arthedain |
| `gruppo` | Nazgûl, Istari, Bianco Consiglio |
| `divinità` | Sauron, Morgoth, Manwë |

Lo stesso vale per i luoghi:

| Tipo | Esempi |
|---|---|
| `città` | Minas Tirith, Edoras |
| `fortezza` | Barad-dûr, Orthanc |
| `regione` | la Contea, Mordor, Rohan |
| `montagna` | Caradhras, Monte Fato |
| `fiume` | Anduin, Brandivino |
| `mare` | Belegaer, Mare di Rhûn |
| `bosco` | Bosco Atro, Fangorn |
| `passo` | l'Alto Passo, il Cancello Nero |

## 6. Come lavora il computer

```
file YAML          →   controllo        →   file JSON        →   sito
(leggibili a mano)     (errori subito)      (per il browser)     (pagine statiche)
```

1. **YAML**: noi scriviamo i dati in file di testo con un formato semplice.
2. **Controllo**: un programma verifica ID doppi, riferimenti inesistenti, date
   impossibili, campi vuoti.
3. **JSON**: il controllo produce la versione "da macchina", compatta.
4. **Sito**: Astro legge il JSON e crea una pagina per ogni evento, persona e luogo.

Il browser non interroga niente: riceve pagine già pronte. Per questo il sito è
veloce e può stare su GitHub Pages gratis.

## 7. Perché non un database "vero"

Un database tradizionale (PostgreSQL, MySQL) ha senso quando:

- più persone scrivono contemporaneamente;
- i dati cambiano ogni minuto;
- servono login, permessi, transazioni.

Qui abbiamo un autore, dati che cambiano quando li correggiamo, e un sito pubblico
che deve solo leggere. Un database server aggiungerebbe costo, manutenzione e un
punto di rottura, senza risolvere nessun problema reale.

Se un giorno vorrai interrogare i dati con SQL per studiarti le parentele, il build
già produce `build/arda.sqlite`: è un database vero, ma **locale**, non online.

## 8. Il primo passo concreto (fatto)

Partiamo dai **luoghi**, non dalle persone.

Motivi:

- sono più stabili delle persone (un fiume non cambia nome in base alla traduzione);
- servono subito per la mappa;
- gli eventi li citano già, quindi il lavoro è classificare e unire i doppioni,
  non trascrivere.

Primo blocco: i **20 luoghi più importanti**. Per ognuno:

1. ID stabile
2. nome visibile
3. tipo
4. alias (nomi alternativi)
5. una riga di descrizione

Poi il controllo: ogni evento che cita quel luogo deve trovare la scheda.
Quando i primi 20 sono validati, passiamo agli altri 20. Alla fine, le persone.

Niente fretta: un blocco alla volta, con il computer che controlla.

## 9. Stato

Anagrafica dei luoghi completa rispetto agli eventi attuali: `data/luoghi.yaml`
contiene **100 schede**, che coprono tutti i nomi di luogo citati dagli eventi
(alcuni nomi sono alias dello stesso luogo). Gli eventi **richiamano i luoghi per
ID**: il build controlla che ogni ID esista e usa il nome solo per la
visualizzazione.

Anagrafica dei partecipanti completa: `data/persone.yaml` contiene **150
personaggi** e `data/entita.yaml` contiene **51 entità collettive**. Insieme
coprono **tutti i 170 nomi** di partecipante citati dagli eventi. Anche i
partecipanti richiamano le schede per ID (`persona:` o `entita:`), come i luoghi.
Le 31 schede in più rispetto ai partecipanti sono i re e i Capitani della Casa di
Isildur: non compaiono negli eventi della Terza Era, ma servono all'albero
genealogico.

Per la Terza Era il database di eventi, luoghi e partecipanti è pronto: **204
eventi**. Il lavoro continua con l'espansione dell'Appendice B: 119 anni su 127
coperti; gli 8 anni restanti sono dentro eventi-intervallo o annotazioni di
regno. Dei Grandi Anni 3018-3019 sono coperti i passaggi principali; restano le
giornate minori e alcuni dettagli del 3020-3021.

Le **parentele** coprono sei gruppi: la Casa di Elrond (pilota), la Casa di
Isildur (la linea settentrionale da Elendil ad Aragorn II), la Casa di Eorl
(i Re del Mark, da Léod a Elfwine il Bello), la Casa di Durin (da Durin I a
Durin VII), la Casa di Húrin (i Sovrintendenti di Gondor, da Húrin di Emyn
Arnen a Faramir, con Dol Amroth) e gli Hobbit (Baggins, Tuc, Brandibuck,
Gamgi, da Gorhendad a Samvise e ai suoi figli).
`data/relazioni.yaml` contiene **280 archi** (241 genitore, 39 coniuge) e collega
**268 persone**. Il build produce `build/alberi.md` (albero leggibile),
`build/rapporto-parentele.md` (controllo) e `build/relazioni.json` (grafo per il
sito). Mancano la linea meridionale di Anárion e i rami collaterali delle tavole
hobbit (Boffin, Bolgeri, Cotton, Rintanati); poi le fonti come entità separate,
le coordinate dei luoghi e la vetrina.

Le date delle tavole hobbit sono nel Calendario della Contea: il build le riceve
già convertite nella Terza Era (anno della Contea + 1600).

### Una nota sui nomi doppi

Tolkien usa più volte gli stessi nomi. Nel database il `nome` deve essere unico,
quindi i due casi finora incontrati portano il regno:

- **Eldacar di Arnor** (il re del Nord) ed **Eldacar** (il re di Gondor);
- **Tarondor di Arnor** (il re del Nord) e **Tarondor** (il re di Gondor).

La tavola dell'Appendice A scrive **Amlalth** e **Argevil**; il testo narrativo
dice **Arvegil**. Il sito usa **Amlaith** e **Arvegil** (le forme corrette) e
registra la variante della tavola nella `nota` della scheda.
