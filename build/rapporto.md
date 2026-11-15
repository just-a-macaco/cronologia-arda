# Rapporto sul lavoro — Terza Era

- Eventi: **204** (erano 51).
- Partecipanti nominati: **170** nomi distinti, 582 presenze.
- Luoghi nominati: **100** nomi distinti.
- Eventi con solo anno (o senza anno): **126**.
- Eventi con nota o certezza non piena: **19**.

## Eventi separati

Alcuni eventi del dataset originale contenevano più avvenimenti distinti.
Sono stati separati perché hanno partecipanti e conseguenze diverse.

- `anello-bilbo` → `consiglio-dol-guldur`, `smaug-ucciso`, `cinque-eserciti`
- `rohan` → `battaglia-celebrant`
- `lungo-inverno` → `saruman-isengard`
- `osgiliath-3018` → `gollum-fugge`
- `fosso-helm` → `distruzione-isengard`
- `distruzione-anello` → `morannon`
- `elessar` → `nozze-elessar-arwen`

## Eventi aggiunti

- `festa-inattesa` — La festa inattesa

## Correzioni di nome

- **Aurighe → Carrieri**: la forma dell'epub è «Carrieri» (9 occorrenze, «Aurighe» 0).
- **Porti Grigi → Rifugi Oscuri**: l'epub usa 18 volte «Rifugi Oscuri»; «Porti Grigi» è la spiegazione.
- **Éorl → Eorl**: l'epub scrive sempre «Eorl», senza accento.
- **Dáin → Dàin**: l'epub usa l'accento grave: «Dàin» (32 occorrenze).
- **Thráin → Thràin**: l'epub usa l'accento grave: «Thràin» (30 occorrenze).
- **Náin → Nain**: l'epub scrive «Nain» senza accento.
- **Rath Dínen → Rath Dinen**: l'epub scrive «Rath Dinen» senza accento.
- **Snowmane → Nevecrino**: nome italiano del cavallo di Théoden.
- **Grima → Grima Vermilinguo**: la forma completa dell'epub.

## Casi da sapere

- **Isildur muore e l'Anello è perduto** (`isildur-anello`): L'Anello resta perduto nel fiume per circa 2.500 anni, fino al 2463.
- **Giungono gli Istari** (`istari`): L'epub non nomina i due Istari azzurri; i loro nomi si trovano in altre opere e vanno trattati come tradizione separata.
- **La Lotta delle Stirpi** (`lotta-stirpi`): La guerra è trattata come un solo evento con intervallo; le singole battaglie (Osgiliath 1436, Erui 1447, Pelargir 1447) possono diventare schede autonome in una fase successiva.
- **I Carrieri travolgono Gondor** (`aurighe`): L'ID storico dell'evento resta `aurighe`, ma il nome visibile è ora «Carrieri», la forma dell'edizione Bompiani 2004.
- **Eärnil I muore in mare** (`earnil-morte-mare`): La voce dell'Appendice dice che Eärnil «si disperse in mare».
- **Osgiliath brucia** (`incendio-osgiliath`): La scheda separa l'incendio dall'evento generale della Lotta delle Stirpi.
- **Il Re degli Stregoni entra a Mordor** (`re-stregoni-mordor`): La caduta di Moria è nella scheda separata sul Balrog.
- **La sparizione di Eärnur** (`earnur`): La sparizione è certa; la morte è presunta, non testimoniata. L'epub alterna «Eärnur» e «Earnur»: si adotta la forma con la dieresi.
- **Osgiliath è distrutta** (`osgiliath-distrutta`): L'Appendice B non nomina gli assalitori; la scheda li indica come «forze di Mordor» in modo generico.
- **Il dono di Calenardhon e il Giuramento di Eorl** (`rohan`): La battaglia e il dono sono due eventi distinti dello stesso anno: hanno partecipanti e conseguenze diverse e vanno tenuti separati.
- **La festa inattesa** (`festa-inattesa`): L'Appendice B data l'impresa al 2941; il testo de Lo Hobbit la colloca in aprile senza indicare il giorno. La scheda non inventa una data più precisa.
- **L'Anello ritrova Bilbo** (`anello-bilbo`): La data esatta non è nell'Appendice B; la cronologia de Lo Hobbit la colloca nell'estate del 2941.
- **Il Bianco Consiglio attacca Dol Guldur** (`consiglio-dol-guldur`): L'Appendice B non descrive lo svolgimento dell'attacco; la scena è narrata in altre opere. La scheda si limita a ciò che dice l'Appendice.
- **La festa d'addio di Bilbo** (`festa-bilbo`): La data è quella del calendario della Contea, come nell'Appendice B.
- **Battaglia del Trombatorrione** (`fosso-helm`): La battaglia inizia il 3 marzo e prosegue fino all'alba del 4; la scheda usa il giorno d'inizio.
- **Battaglia dei Campi del Pelennor** (`pelennor`): Nomi verificati sull'epub: Nevecrino (non Snowmane), Casa dei Sovrintendenti (singolare), Rath Dinen, Sudroni, Dernhelm, Harlond.
- **Nozze di Elessar e Arwen** (`nozze-elessar-arwen`): La data esatta segue il calendario della Contea; il testo la indica come «Giorno di Mezza Estate».
- **Battaglia di Lungacque** (`lungacque`): «Grima Vermilinguo» è la forma dell'edizione Bompiani, verificata sull'epub.
- **La partenza dai Rifugi Oscuri** (`porti-grigi`): Il titolo usa «Rifugi Oscuri», la forma dell'edizione Bompiani. L'ID storico resta `porti-grigi`.

## Cosa manca ancora

- I partecipanti sono collegati agli eventi tramite ID; le schede persona
  ed entità collettiva sono pronte. Le parentele sono cominciate con la
  Casa di Elrond (`data/relazioni.yaml`); mancano le altre casate e le fonti
  come entità separate.
- I luoghi sono ora collegati agli eventi tramite ID: la fase mappa assegnerà
  coordinate e scene (Arda piatta / Arda rotonda).
- Gli eventi del 2941 e del 3019 sono stati separati, ma restano da aggiungere
  gli altri fatti dell'Appendice B (battaglie del Nord, assalti a Lórien,
  distruzione di Dol Guldur, Campo di Cormallen).
- Le date con solo l'anno non hanno giorno e mese: è voluto, non è una lacuna
  del lavoro. Il sito deve mostrarle come «anno» e non inventare precisione.
