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
# data/persone/frodo-baggins.yaml
id: frodo-baggins
nome: Frodo Baggins
tipo: personaggio
popolo: Hobbit
nascita: 2968
morte: null
alias:
  - Frodo
```

### Un luogo

```yaml
# data/luoghi/contea.yaml
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

- sono 85, non 112;
- sono più stabili (un fiume non cambia nome in base alla traduzione);
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
contiene 77 schede, che coprono tutti gli 85 nomi citati dagli eventi (alcuni nomi
sono alias dello stesso luogo). Gli eventi ora **richiamano i luoghi per ID**: il
build controlla che ogni ID esista e usa il nome solo per la visualizzazione.

Anagrafica dei partecipanti completa: `data/persone.yaml` contiene **90 personaggi**
e `data/entita.yaml` contiene **43 entità collettive**. Insieme coprono **tutti i
133 nomi** di partecipante citati dagli eventi. Anche i partecipanti richiamano le
schede per ID (`persona:` o `entita:`), come i luoghi.

Per la Terza Era il database di eventi, luoghi e partecipanti è pronto. Il lavoro
continua con l'espansione dell'Appendice B: 90 eventi e 64 anni su 127 coperti.
Restano le famiglie (per gli alberi genealogici), le fonti come entità separate e
la vetrina.
