# Rapporto sulle parentele

- Relazioni registrate: **57**.
  - genitore: **52**.
  - coniuge: **5**.
- Persone collegate: **52** su **150**.
- Gruppi familiari (componenti): **1**.
- Coppie di fratelli ricavate dai genitori comuni: **4**.
- Persone con genere dichiarato: **52**.

## Controlli superati

- Ogni relazione rimanda a due persone che esistono.
- Nessuna persona è genitore di se stessa.
- Nessun ciclo: nessuno è antenato di se stesso.
- Ogni figlio ha al massimo un padre e una madre.
- Nessun genitore è nato prima o nello stesso anno del figlio.
- Nessuna coppia di coniugi è registrata due volte.
- Ogni persona citata in una relazione ha il genere dichiarato.

## Gruppi familiari

| Gruppo | Membri | Radici |
|---|---|---|
| 1 | Amlaith, Anárion, Arador, Araglas, Aragorn, Aragorn I, Aragost, Arahad I, Arahad II, Arahael, Aranarth, Arantar, Aranuir, Araphant, Araphor, Arassuil, Arathorn I, Arathorn II, Araval, Aravir, Aravorn, Argeleb I, Argeleb II, Argonui, Arvedui, Arvegil, Arveleg I, Arveleg II, Arwen, Beleg, Celeborn, Celebrindor, Celebrían, Celepharn, Eldacar di Arnor, Elendil, Elendur, Elladan, Elrohir, Elrond, Eärendur, Firiel, Galadriel, Gilraen, Isildur, Mallor, Malvegil, Meneldil, Tarcil, Tarondor di Arnor, Valandil, Valandur | Celeborn ⚭ Galadriel; Elendil |

## Persone collegate

| Persona | Genere | Genitori | Coniugi | Figli |
|---|---|---|---|---|
| Amlaith | m | Eärendur | — | Beleg |
| Anárion | m | Elendil | — | Meneldil |
| Arador | m | Argonui | — | Arathorn II |
| Araglas | m | Aragorn I | — | Arahad I |
| Aragorn | m | Arathorn II, Gilraen | Arwen | — |
| Aragorn I | m | Aravir | — | Araglas |
| Aragost | m | Arahad I | — | Aravorn |
| Arahad I | m | Araglas | — | Aragost |
| Arahad II | m | Aravorn | — | Arassuil |
| Arahael | m | Aranarth | — | Aranuir |
| Aranarth | m | Arvedui, Firiel | — | Arahael |
| Arantar | m | Eldacar di Arnor | — | Tarcil |
| Aranuir | m | Arahael | — | Aravir |
| Araphant | m | Araval | — | Arvedui |
| Araphor | m | Arveleg I | — | Argeleb II |
| Arassuil | m | Arahad II | — | Arathorn I |
| Arathorn I | m | Arassuil | — | Argonui |
| Arathorn II | m | Arador | Gilraen | Aragorn |
| Araval | m | Arveleg II | — | Araphant |
| Aravir | m | Aranuir | — | Aragorn I |
| Aravorn | m | Aragost | — | Arahad II |
| Argeleb I | m | Malvegil | — | Arveleg I |
| Argeleb II | m | Araphor | — | Arvegil |
| Argonui | m | Arathorn I | — | Arador |
| Arvedui | m | Araphant | Firiel | Aranarth |
| Arvegil | m | Argeleb II | — | Arveleg II |
| Arveleg I | m | Argeleb I | — | Araphor |
| Arveleg II | m | Arvegil | — | Araval |
| Arwen | f | Celebrían, Elrond | Aragorn | — |
| Beleg | m | Amlaith | — | Mallor |
| Celeborn | m | — | Galadriel | Celebrían |
| Celebrindor | m | Celepharn | — | Malvegil |
| Celebrían | f | Celeborn, Galadriel | Elrond | Arwen, Elladan, Elrohir |
| Celepharn | m | Mallor | — | Celebrindor |
| Eldacar di Arnor | m | Valandil | — | Arantar |
| Elendil | m | — | — | Anárion, Isildur |
| Elendur | m | Valandur | — | Eärendur |
| Elladan | m | Celebrían, Elrond | — | — |
| Elrohir | m | Celebrían, Elrond | — | — |
| Elrond | m | — | Celebrían | Arwen, Elladan, Elrohir |
| Eärendur | m | Elendur | — | Amlaith |
| Firiel | f | — | Arvedui | Aranarth |
| Galadriel | f | — | Celeborn | Celebrían |
| Gilraen | f | — | Arathorn II | Aragorn |
| Isildur | m | Elendil | — | Valandil |
| Mallor | m | Beleg | — | Celepharn |
| Malvegil | m | Celebrindor | — | Argeleb I |
| Meneldil | m | Anárion | — | — |
| Tarcil | m | Arantar | — | Tarondor di Arnor |
| Tarondor di Arnor | m | Tarcil | — | Valandur |
| Valandil | m | Isildur | — | Eldacar di Arnor |
| Valandur | m | Tarondor di Arnor | — | Elendur |

## Limiti noti

- Le parentele coperte sono due casate: la Casa di Elrond e la Casa di
  Isildur (linea settentrionale, da Elendil ad Aragorn II). Mancano Rohan,
  Durin, i Sovrintendenti, gli Hobbit e la linea meridionale di Anárion.
- L'albero testuale non sa disegnare un matrimonio che unisce due casate:
  quando una persona compare già sotto un'altra discendenza, la riga lo
  segnala con «(già mostrato sopra)». Il grafo completo è in
  `build/relazioni.json`.
- Una persona con più coniugi viene raggruppata in un unico nodo. Quando
  servirà, i matrimoni andranno separati con un identificativo proprio.
- I fratelli sono ricavati dai genitori comuni e non hanno una distinzione
  tra fratelli pieni e fratellastri.

## Persone non ancora collegate

Sono **98**. Verranno aggiunte una casata alla volta.

<details>
<summary>Mostra l'elenco</summary>

- Gollum
- Thorin Scudodiquercia
- Gimli
- Bilbo Baggins
- Théoden
- Finduilas
- Frodo Baggins
- Boromir
- Samvise Gamgi
- Meriadoc Brandibuck
- Faramir
- Peregrino Tuc
- Éomer
- Éowyn
- Elanor
- Adrahil
- Aldamir
- Amroth
- Bain
- Baldor
- Balin
- Barbalbero
- Bard
- Bard II
- Belecthor II
- Beregond
- Brand
- Brandobras Tuc
- Brego
- Bucca della Palude
- Calimehtar
- Castamir
- Cirion
- Ciryandil
- Círdan
- Denethor II
- Durin VI
- Dàin I
- Dàin Piediferro
- Déagol
- Ecthelion I
- Ecthelion II
- Eldacar
- Eorl il Giovane
- Eärnil
- Eärnil I
- Eärnur
- Falastur
- Folcwine
- Frumgar
- Fréaláf
- Gandalf
- Gerontius Tuc
- Gil-galad
- Glorfindel
- Grór
- Helm
- Hyarmendacil
- Hyarmendacil II
- Imrahil
- Isengrim II
- Isumbras I
- Legolas
- Mardil
- Minardil
- Nain I
- Narmacil II
- Nár
- Ohtar
- Ondoher
- Ornendil
- Ostoher
- Radagast
- Rosie Cotton
- Rómendacil I
- Saruman
- Sauron
- Shelob
- Smaug
- Tarondor
- Telemnar
- Telumehtar Umbardacil
- Thengel
- Thorin I
- Thorin III Elminpietra
- Thranduil
- Thràin I
- Thràin II
- Thrór
- Théodred
- Tobaldo
- Tom Bombadil
- Valacar
- Walda
- Wulf
- il Balrog
- il Re degli Stregoni
- un Orchetto di Moria

</details>
