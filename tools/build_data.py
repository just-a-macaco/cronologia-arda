#!/usr/bin/env python3
"""Compila le schede degli eventi in dati per il sito.

Legge i file YAML in data/eventi/, data/luoghi.yaml, data/persone.yaml e
data/entita.yaml, controlla i riferimenti e produce:
  - js/data.js                 (formato compatibile con js/circle.js)
  - build/arda.sqlite          (database interrogabile con SQL)
  - build/indexes.json         (indici per ricerca e filtri)
  - build/luoghi.json          (anagrafica dei luoghi e copertura degli eventi)
  - build/persone.json         (anagrafica dei personaggi e copertura)
  - build/entita.json          (popoli, regni e gruppi)
  - build/schede-terza-era.md  (le schede in forma leggibile)
  - build/rapporto.md          (riepilogo del lavoro)
  - build/rapporto-luoghi.md   (stato dell'anagrafica dei luoghi)
  - build/rapporto-persone.md  (stato dell'anagrafica dei personaggi)
  - build/rapporto-entita.md   (stato delle entità collettive)
  - build/rapporto-partecipanti.md (copertura complessiva dei partecipanti)
  - build/rapporto-dati.md     (controllo complessivo del database)
  - build/relazioni.json       (grafo delle parentele per il sito)
  - build/rapporto-parentele.md (stato delle parentele)
  - build/alberi.md            (alberi genealogici in forma testuale)

Uso: python3 tools/build_data.py
"""
from __future__ import annotations

import glob
import json
import os
import sqlite3
import sys
from collections import Counter
from datetime import date

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "eventi")
LUOGHI_FILE = os.path.join(ROOT, "data", "luoghi.yaml")
PERSONE_FILE = os.path.join(ROOT, "data", "persone.yaml")
ENTITA_FILE = os.path.join(ROOT, "data", "entita.yaml")
RELAZIONI_FILE = os.path.join(ROOT, "data", "relazioni.yaml")
BUILD_DIR = os.path.join(ROOT, "build")
JS_DIR = os.path.join(ROOT, "js")

NOMI_ERA = {
    "lampade": "Era delle Lampadi",
    "alberi": "Era degli Alberi",
    "prima": "Prima Era",
    "seconda": "Seconda Era",
    "terza": "Terza Era",
    "quarta": "Quarta Era",
}

TIPI = {
    "evento", "fondazione", "battaglia", "guerra", "distruzione", "perdita",
    "tradimento", "morte", "nascita", "viaggio", "consiglio", "politica",
}
TIPI_LUOGO = {
    "regione", "regno", "città", "villaggio", "rifugio", "edificio", "fortezza",
    "torre", "montagna", "collina", "fiume", "bosco", "valle", "porto",
    "città sotterranea", "passo", "pianura", "palude", "caverna", "ponte",
    "monumento", "mondo", "mare",
}
TIPI_PERSONA = {"personaggio", "popolo", "regno", "gruppo"}
TIPI_ENTITA = {"popolo", "regno", "gruppo"}
SPECIE = {"Hobbit", "Uomo", "Elfo", "Nano", "Maia", "Sturoi", "Mezzelfo", "Drago", "Ent", "Orchetto", "Ragno"}
GENERI = {"m", "f"}
TIPI_RELAZIONE = {"genitore", "coniuge"}
PRECISIONI = {"giorno", "mese", "anno", "intervallo", "ignoto"}
QUALIFICATORI = {None, "circa", "prima", "dopo", "inizio", "fine"}

# ID presenti nel dataset originale (js/data.js prima di questo build).
ID_ORIGINALI = {
    "inizio-terza", "isildur-anello", "divisione-arnor", "istari",
    "ombra-bosco-attro", "saggi-dol-guldur", "angmar", "angmar-invaude",
    "lotta-stirpi", "grande-peste", "mordor-sorveglianza", "aurighe",
    "battaglia-campo", "cade-arnor", "battaglia-fornost", "balrog-moria",
    "nani-erebor", "minas-ithil", "earnur", "pace-vigile", "sauron-ritorno",
    "deagol-anello", "osgiliath-distrutta", "rohan", "draghi-nord",
    "erba-pipa", "lungo-inverno", "smaug-erebor", "thror", "nanduhirion",
    "gandalf-dol-guldur", "bilbo-nasce", "anello-bilbo", "bilbo-torna",
    "sauron-si-dichiara", "ultimo-consiglio", "fato-avvampa",
    "saruman-tradisce", "festa-bilbo", "osgiliath-3018", "frodo-parte",
    "consiglio-elrond", "compagnia-parte", "gandalf-moria",
    "compagnia-si-scioglie", "fosso-helm", "pelennor",
    "distruzione-anello", "elessar", "lungacque", "porti-grigi",
}

# Eventi nati dalla separazione di un evento che ne conteneva più d'uno.
SEPARAZIONI = {
    "anello-bilbo": ["consiglio-dol-guldur", "smaug-ucciso", "cinque-eserciti"],
    "rohan": ["battaglia-celebrant"],
    "lungo-inverno": ["saruman-isengard"],
    "osgiliath-3018": ["gollum-fugge"],
    "fosso-helm": ["distruzione-isengard"],
    "distruzione-anello": ["morannon"],
    "elessar": ["nozze-elessar-arwen"],
}
AGGIUNTI = {"festa-inattesa"}

# Correzioni di nome fatte rispetto al dataset/glossario precedente.
CORREZIONI = [
    ("Aurighe", "Carrieri", "la forma dell'epub è «Carrieri» (9 occorrenze, «Aurighe» 0)"),
    ("Porti Grigi", "Rifugi Oscuri", "l'epub usa 18 volte «Rifugi Oscuri»; «Porti Grigi» è la spiegazione"),
    ("Éorl", "Eorl", "l'epub scrive sempre «Eorl», senza accento"),
    ("Dáin", "Dàin", "l'epub usa l'accento grave: «Dàin» (32 occorrenze)"),
    ("Thráin", "Thràin", "l'epub usa l'accento grave: «Thràin» (30 occorrenze)"),
    ("Náin", "Nain", "l'epub scrive «Nain» senza accento"),
    ("Rath Dínen", "Rath Dinen", "l'epub scrive «Rath Dinen» senza accento"),
    ("Snowmane", "Nevecrino", "nome italiano del cavallo di Théoden"),
    ("Grima", "Grima Vermilinguo", "la forma completa dell'epub"),
]


def fail(msg: str) -> None:
    print(f"ERRORE: {msg}", file=sys.stderr)
    raise SystemExit(1)


def carica() -> list[dict]:
    eventi: list[dict] = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.yaml"))):
        with open(path, encoding="utf-8") as fh:
            blocco = yaml.safe_load(fh)
        if not isinstance(blocco, list):
            fail(f"{path}: il file deve contenere una lista di eventi")
        for ev in blocco:
            ev["_file"] = os.path.basename(path)
            eventi.append(ev)
    if not eventi:
        fail("nessun evento trovato in data/eventi/")
    return eventi


def valida(eventi: list[dict]) -> None:
    ids: set[str] = set()
    for ev in eventi:
        eid = ev.get("id", "?")
        if not eid or not isinstance(eid, str):
            fail(f"{ev['_file']}: evento senza id")
        if eid in ids:
            fail(f"id duplicato: {eid}")
        ids.add(eid)
        for campo in ("titolo", "tipo", "breve", "lungo", "certezza", "fonti", "luoghi", "partecipanti"):
            if campo not in ev or ev[campo] in (None, "", []):
                fail(f"{eid}: campo mancante o vuoto «{campo}»")
        if ev["tipo"] not in TIPI:
            fail(f"{eid}: tipo sconosciuto «{ev['tipo']}»")
        d = ev.get("data") or {}
        for campo in ("era", "anno", "precisione", "calendario", "testo"):
            if campo not in d or d[campo] in (None, ""):
                fail(f"{eid}: data mancante «{campo}»")
        if not isinstance(d["anno"], int):
            fail(f"{eid}: anno non intero")
        if d["precisione"] not in PRECISIONI:
            fail(f"{eid}: precisione sconosciuta «{d['precisione']}»")
        if d.get("qualificatore") not in QUALIFICATORI:
            fail(f"{eid}: qualificatore sconosciuto «{d.get('qualificatore')}»")
        m, g = d.get("mese"), d.get("giorno")
        if m is not None and not (1 <= m <= 12):
            fail(f"{eid}: mese fuori intervallo")
        if g is not None:
            if m is None:
                fail(f"{eid}: giorno senza mese")
            try:
                date(d["anno"], m, g)
            except ValueError:
                fail(f"{eid}: giorno non valido ({d['anno']}-{m}-{g})")
        fine = d.get("anno_fine")
        if fine is not None and fine < d["anno"]:
            fail(f"{eid}: anno_fine precedente all'anno")
        if d["precisione"] == "intervallo" and fine is None:
            fail(f"{eid}: intervallo senza anno_fine")
        for p in ev["partecipanti"]:
            if not (p.get("persona") or p.get("entita")):
                fail(f"{eid}: partecipante senza «persona» o «entita»")
            if p.get("persona") and p.get("entita"):
                fail(f"{eid}: partecipante con «persona» ed «entita» insieme")
            if not p.get("ruolo"):
                fail(f"{eid}: partecipante senza ruolo")
            if not p.get("parte"):
                fail(f"{eid}: partecipante senza parte")
        for f in ev["fonti"]:
            if not f.get("opera") or not f.get("riferimento"):
                fail(f"{eid}: fonte incompleta")
        if len(ev["breve"]) < 20:
            fail(f"{eid}: testo breve troppo corto")
        if len(ev["lungo"]) < len(ev["breve"]):
            fail(f"{eid}: il testo lungo è più corto del breve")


def carica_luoghi() -> list[dict]:
    if not os.path.exists(LUOGHI_FILE):
        fail("manca data/luoghi.yaml")
    with open(LUOGHI_FILE, encoding="utf-8") as fh:
        blocco = yaml.safe_load(fh)
    if not isinstance(blocco, list):
        fail("data/luoghi.yaml deve contenere una lista di luoghi")
    return blocco


def valida_luoghi(luoghi: list[dict]) -> None:
    ids: set[str] = set()
    nomi: dict[str, str] = {}
    alias_visti: dict[str, str] = {}
    for luogo in luoghi:
        lid = luogo.get("id", "?")
        for campo in ("id", "nome", "tipo", "descrizione"):
            if not luogo.get(campo):
                fail(f"luogo {lid}: campo mancante o vuoto «{campo}»")
        if luogo["tipo"] not in TIPI_LUOGO:
            fail(f"luogo {lid}: tipo sconosciuto «{luogo['tipo']}»")
        if lid in ids:
            fail(f"luogo con id duplicato: {lid}")
        ids.add(lid)
        if luogo["nome"] in nomi:
            fail(f"luogo con nome duplicato: {luogo['nome']} ({nomi[luogo['nome']]} e {lid})")
        nomi[luogo["nome"]] = lid
        alias = luogo.get("alias") or []
        if not isinstance(alias, list):
            fail(f"luogo {lid}: «alias» deve essere una lista")
        for nome_alias in alias:
            if nome_alias in alias_visti and alias_visti[nome_alias] != lid:
                fail(f"alias «{nome_alias}» usato da {alias_visti[nome_alias]} e {lid}")
            alias_visti[nome_alias] = lid
    for nome, lid in nomi.items():
        if nome in alias_visti and alias_visti[nome] != lid:
            fail(f"«{nome}» è nome di {lid} ma anche alias di {alias_visti[nome]}")
    for luogo in luoghi:
        dentro = luogo.get("dentro")
        if dentro is not None and dentro not in ids:
            fail(f"luogo {luogo['id']}: «dentro» rimanda a {dentro}, che non esiste")
        if dentro == luogo["id"]:
            fail(f"luogo {luogo['id']}: un luogo non può stare dentro se stesso")
        visto = set()
        corrente = luogo
        while corrente.get("dentro"):
            if corrente["id"] in visto:
                fail(f"luogo {luogo['id']}: gerarchia circolare")
            visto.add(corrente["id"])
            corrente = next((l for l in luoghi if l["id"] == corrente["dentro"]), {})


def valida_riferimenti_luoghi(eventi: list[dict], luoghi: list[dict]) -> None:
    ids = {luogo["id"] for luogo in luoghi}
    for ev in eventi:
        for lid in ev["luoghi"]:
            if lid not in ids:
                fail(f"{ev['id']}: luogo sconosciuto «{lid}»")


def indice_nomi_luoghi(luoghi: list[dict]) -> dict[str, str]:
    indice: dict[str, str] = {}
    for luogo in luoghi:
        indice[luogo["nome"]] = luogo["id"]
        for nome_alias in luogo.get("alias") or []:
            indice[nome_alias] = luogo["id"]
    return indice


def collega_luoghi(eventi: list[dict], luoghi: list[dict]) -> dict:
    ids = {luogo["id"] for luogo in luoghi}
    citati: set[str] = set()
    per_luogo: dict[str, set[str]] = {}
    for ev in eventi:
        for lid in ev["luoghi"]:
            citati.add(lid)
            per_luogo.setdefault(lid, set()).add(ev["id"])
    scoperti = citati - ids
    schede = []
    for luogo in luoghi:
        record = dict(luogo)
        record["eventi"] = sorted(per_luogo.get(luogo["id"], set()))
        schede.append(record)
    return {
        "schede": schede,
        "citati": citati,
        "scoperti": scoperti,
        "per_luogo": {k: sorted(v) for k, v in per_luogo.items()},
    }


def carica_persone() -> list[dict]:
    if not os.path.exists(PERSONE_FILE):
        fail("manca data/persone.yaml")
    with open(PERSONE_FILE, encoding="utf-8") as fh:
        blocco = yaml.safe_load(fh)
    if not isinstance(blocco, list):
        fail("data/persone.yaml deve contenere una lista di persone")
    return blocco


def valida_persone(persone: list[dict]) -> None:
    ids: set[str] = set()
    nomi: dict[str, str] = {}
    alias_visti: dict[str, str] = {}
    for persona in persone:
        pid = persona.get("id", "?")
        for campo in ("id", "nome", "tipo", "descrizione"):
            if not persona.get(campo):
                fail(f"persona {pid}: campo mancante o vuoto «{campo}»")
        if persona["tipo"] not in TIPI_PERSONA:
            fail(f"persona {pid}: tipo sconosciuto «{persona['tipo']}»")
        if persona["tipo"] == "personaggio" and persona.get("specie") not in SPECIE:
            fail(f"persona {pid}: specie mancante o sconosciuta «{persona.get('specie')}»")
        if persona.get("specie") is not None and persona["specie"] not in SPECIE:
            fail(f"persona {pid}: specie sconosciuta «{persona['specie']}»")
        if persona.get("genere") is not None and persona["genere"] not in GENERI:
            fail(f"persona {pid}: genere sconosciuto «{persona['genere']}»")
        for campo in ("nascita", "morte"):
            valore = persona.get(campo)
            if valore is not None and not isinstance(valore, int):
                fail(f"persona {pid}: «{campo}» deve essere un anno o null")
        if persona.get("nascita") is not None and persona.get("morte") is not None:
            if persona["morte"] < persona["nascita"]:
                fail(f"persona {pid}: morte precedente alla nascita")
        if pid in ids:
            fail(f"persona con id duplicato: {pid}")
        ids.add(pid)
        if persona["nome"] in nomi:
            fail(f"persona con nome duplicato: {persona['nome']} ({nomi[persona['nome']]} e {pid})")
        nomi[persona["nome"]] = pid
        alias = persona.get("alias") or []
        if not isinstance(alias, list):
            fail(f"persona {pid}: «alias» deve essere una lista")
        for nome_alias in alias:
            if nome_alias in alias_visti and alias_visti[nome_alias] != pid:
                fail(f"alias «{nome_alias}» usato da {alias_visti[nome_alias]} e {pid}")
            alias_visti[nome_alias] = pid
    for nome, pid in nomi.items():
        if nome in alias_visti and alias_visti[nome] != pid:
            fail(f"«{nome}» è nome di {pid} ma anche alias di {alias_visti[nome]}")


def indice_nomi_persone(persone: list[dict]) -> dict[str, str]:
    indice: dict[str, str] = {}
    for persona in persone:
        indice[persona["nome"]] = persona["id"]
        for nome_alias in persona.get("alias") or []:
            indice[nome_alias] = persona["id"]
    return indice


def collega_persone(eventi: list[dict], persone: list[dict]) -> dict:
    indice = indice_nomi_persone(persone)
    citazioni: dict[str, list[str]] = {}
    for ev in eventi:
        for partecipante in ev["partecipanti"]:
            nome = partecipante["nome"]
            citazioni.setdefault(nome, []).append(ev["id"])
    coperti = {nome: indice[nome] for nome in citazioni if nome in indice}
    scoperti = {nome: ids for nome, ids in citazioni.items() if nome not in indice}
    per_persona: dict[str, set[str]] = {}
    for nome, pid in coperti.items():
        per_persona.setdefault(pid, set()).update(citazioni[nome])
    schede = []
    for persona in persone:
        record = dict(persona)
        record["eventi"] = sorted(per_persona.get(persona["id"], set()))
        schede.append(record)
    return {
        "schede": schede,
        "coperti": coperti,
        "scoperti": scoperti,
        "per_persona": {k: sorted(v) for k, v in per_persona.items()},
    }


def carica_entita() -> list[dict]:
    if not os.path.exists(ENTITA_FILE):
        fail("manca data/entita.yaml")
    with open(ENTITA_FILE, encoding="utf-8") as fh:
        blocco = yaml.safe_load(fh)
    if not isinstance(blocco, list):
        fail("data/entita.yaml deve contenere una lista di entità")
    return blocco


def valida_entita(entita: list[dict]) -> None:
    ids: set[str] = set()
    nomi: dict[str, str] = {}
    alias_visti: dict[str, str] = {}
    for voce in entita:
        eid = voce.get("id", "?")
        for campo in ("id", "nome", "tipo", "descrizione"):
            if not voce.get(campo):
                fail(f"entità {eid}: campo mancante o vuoto «{campo}»")
        if voce["tipo"] not in TIPI_ENTITA:
            fail(f"entità {eid}: tipo sconosciuto «{voce['tipo']}»")
        if eid in ids:
            fail(f"entità con id duplicato: {eid}")
        ids.add(eid)
        if voce["nome"] in nomi:
            fail(f"entità con nome duplicato: {voce['nome']} ({nomi[voce['nome']]} e {eid})")
        nomi[voce["nome"]] = eid
        alias = voce.get("alias") or []
        if not isinstance(alias, list):
            fail(f"entità {eid}: «alias» deve essere una lista")
        for nome_alias in alias:
            if nome_alias in alias_visti and alias_visti[nome_alias] != eid:
                fail(f"alias «{nome_alias}» usato da {alias_visti[nome_alias]} e {eid}")
            alias_visti[nome_alias] = eid
    for nome, eid in nomi.items():
        if nome in alias_visti and alias_visti[nome] != eid:
            fail(f"«{nome}» è nome di {eid} ma anche alias di {alias_visti[nome]}")


def valida_nomi_unici(persone: list[dict], entita: list[dict]) -> None:
    visti: dict[str, str] = {}
    for voce in persone + entita:
        chiavi = [voce["nome"]] + (voce.get("alias") or [])
        for chiave in chiavi:
            if chiave in visti and visti[chiave] != voce["id"]:
                fail(f"«{chiave}» è usato da {visti[chiave]} e {voce['id']}")
            visti[chiave] = voce["id"]


def valida_riferimenti_partecipanti(eventi: list[dict], persone: list[dict], entita: list[dict]) -> None:
    persone_per_id = {p["id"]: p for p in persone}
    entita_per_id = {e["id"]: e for e in entita}
    for ev in eventi:
        for p in ev["partecipanti"]:
            if p.get("persona"):
                if p["persona"] not in persone_per_id:
                    fail(f"{ev['id']}: persona sconosciuta «{p['persona']}»")
            else:
                if p["entita"] not in entita_per_id:
                    fail(f"{ev['id']}: entità sconosciuta «{p['entita']}»")


def carica_relazioni() -> list[dict]:
    if not os.path.exists(RELAZIONI_FILE):
        return []
    with open(RELAZIONI_FILE, encoding="utf-8") as fh:
        blocco = yaml.safe_load(fh) or []
    if not isinstance(blocco, list):
        fail("data/relazioni.yaml deve contenere una lista di relazioni")
    return blocco


def valida_relazioni(relazioni: list[dict], persone: list[dict]) -> None:
    per_id = {p["id"]: p for p in persone}
    visti_genitori: set[tuple[str, str]] = set()
    visti_coniugi: set[tuple[str, str]] = set()
    genitori: dict[str, list[str]] = {}
    for indice, rel in enumerate(relazioni, 1):
        etichetta = f"relazione {indice}"
        for campo in ("da", "a", "tipo", "certezza", "fonti"):
            if not rel.get(campo):
                fail(f"{etichetta}: campo mancante o vuoto «{campo}»")
        if rel["tipo"] not in TIPI_RELAZIONE:
            fail(f"{etichetta}: tipo sconosciuto «{rel['tipo']}»")
        for chiave in ("da", "a"):
            if rel[chiave] not in per_id:
                fail(f"{etichetta}: persona sconosciuta «{rel[chiave]}»")
        if rel["da"] == rel["a"]:
            fail(f"{etichetta}: una persona non può essere parente di se stessa")
        for chiave in ("da", "a"):
            if per_id[rel[chiave]].get("genere") not in GENERI:
                fail(f"{etichetta}: {rel[chiave]} deve avere «genere: m» o «genere: f»")
        if not isinstance(rel["fonti"], list):
            fail(f"{etichetta}: «fonti» deve essere una lista")
        if rel["tipo"] == "genitore":
            chiave = (rel["da"], rel["a"])
            if chiave in visti_genitori:
                fail(f"{etichetta}: relazione genitore duplicata ({rel['da']} → {rel['a']})")
            visti_genitori.add(chiave)
            genitori.setdefault(rel["a"], []).append(rel["da"])
        else:
            chiave = tuple(sorted((rel["da"], rel["a"])))
            if chiave in visti_coniugi:
                fail(f"{etichetta}: coniugi registrati due volte ({rel['da']} e {rel['a']})")
            visti_coniugi.add(chiave)
        for fonte in rel["fonti"]:
            if not fonte.get("opera") or not fonte.get("riferimento"):
                fail(f"{etichetta}: fonte incompleta")
    for figlio, padrini in genitori.items():
        generi = [per_id[p]["genere"] for p in padrini]
        if generi.count("m") > 1:
            fail(f"{figlio}: più di un padre")
        if generi.count("f") > 1:
            fail(f"{figlio}: più di una madre")
        for genitore in padrini:
            anno_genitore = per_id[genitore].get("nascita")
            anno_figlio = per_id[figlio].get("nascita")
            if anno_genitore is not None and anno_figlio is not None and anno_genitore >= anno_figlio:
                fail(f"{genitore} non può essere genitore di {figlio}: nato prima o nello stesso anno")
    finiti: set[str] = set()

    def visita(nodo: str, in_corso: set[str]) -> None:
        if nodo in finiti:
            return
        if nodo in in_corso:
            fail(f"parentela circolare intorno a {nodo}")
        in_corso.add(nodo)
        for genitore in genitori.get(nodo, []):
            visita(genitore, in_corso)
        in_corso.remove(nodo)
        finiti.add(nodo)

    for nodo in genitori:
        visita(nodo, set())


def _ordine_persona(persona: dict) -> tuple:
    """Ordine di lettura: prima chi ha una data di nascita, poi il nome."""
    return (persona.get("nascita") is None, persona.get("nascita") or 0, persona["nome"])


def costruisci_parentele(persone: list[dict], relazioni: list[dict]) -> dict:
    per_id = {p["id"]: p for p in persone}
    figli: dict[str, set[str]] = {}
    genitori: dict[str, set[str]] = {}
    coniugi: dict[str, set[str]] = {}
    adiacenza: dict[str, set[str]] = {}
    for rel in relazioni:
        a, b = rel["da"], rel["a"]
        adiacenza.setdefault(a, set()).add(b)
        adiacenza.setdefault(b, set()).add(a)
        if rel["tipo"] == "genitore":
            figli.setdefault(a, set()).add(b)
            genitori.setdefault(b, set()).add(a)
        else:
            coniugi.setdefault(a, set()).add(b)
            coniugi.setdefault(b, set()).add(a)
    fratelli: dict[str, set[str]] = {}
    for suoi_figli in figli.values():
        for x in suoi_figli:
            for y in suoi_figli:
                if x != y:
                    fratelli.setdefault(x, set()).add(y)
    visti: set[str] = set()
    componenti: list[list[str]] = []
    for partenza in sorted(adiacenza, key=lambda pid: per_id[pid]["nome"]):
        if partenza in visti:
            continue
        coda = [partenza]
        visti.add(partenza)
        membri = []
        while coda:
            corrente = coda.pop()
            membri.append(corrente)
            for vicino in sorted(adiacenza[corrente]):
                if vicino not in visti:
                    visti.add(vicino)
                    coda.append(vicino)
        componenti.append(sorted(membri, key=lambda pid: _ordine_persona(per_id[pid])))
    return {
        "per_id": per_id,
        "figli": figli,
        "genitori": genitori,
        "coniugi": coniugi,
        "fratelli": fratelli,
        "componenti": componenti,
        "collegate": set(adiacenza),
    }


def _unita_coniugi(componente: list[str], coniugi: dict[str, set[str]]) -> tuple[dict[str, frozenset], list[frozenset]]:
    capo = {pid: pid for pid in componente}

    def trova(x: str) -> str:
        while capo[x] != x:
            capo[x] = capo[capo[x]]
            x = capo[x]
        return x

    for pid in componente:
        for altro in coniugi.get(pid, set()):
            if altro not in capo:
                continue
            ra, rb = trova(pid), trova(altro)
            if ra != rb:
                capo[rb] = ra
    gruppi: dict[str, list[str]] = {}
    for pid in componente:
        gruppi.setdefault(trova(pid), []).append(pid)
    unita = [frozenset(gruppo) for gruppo in gruppi.values()]
    unita_di = {pid: gruppo for gruppo in unita for pid in gruppo}
    return unita_di, unita


def _nome_unita(unita: frozenset, per_id: dict[str, dict], principale: str | None = None) -> str:
    if principale is not None and principale in unita:
        nomi = [per_id[principale]["nome"]] + sorted(
            per_id[pid]["nome"] for pid in unita if pid != principale
        )
    else:
        nomi = sorted(per_id[pid]["nome"] for pid in unita)
    return " ⚭ ".join(nomi)


def _radici_unita(
    componente: list[str],
    per_id: dict[str, dict],
    genitori: dict[str, set[str]],
    coniugi: dict[str, set[str]],
) -> tuple[list[frozenset], dict[str, frozenset]]:
    unita_di, unita = _unita_coniugi(componente, coniugi)
    radici = [g for g in unita if all(not genitori.get(pid) for pid in g)]
    radici.sort(key=lambda g: min(_ordine_persona(per_id[pid]) for pid in g))
    return radici, unita_di


def _figli_unita(
    unita: frozenset,
    figli: dict[str, set[str]],
    unita_di: dict[str, frozenset],
    per_id: dict[str, dict],
) -> list[str]:
    trovati: set[str] = set()
    for pid in unita:
        for figlio in figli.get(pid, set()):
            if unita_di[figlio] != unita:
                trovati.add(figlio)
    return sorted(trovati, key=lambda pid: _ordine_persona(per_id[pid]))


def _albero_componente(
    componente: list[str],
    per_id: dict[str, dict],
    figli: dict[str, set[str]],
    genitori: dict[str, set[str]],
    coniugi: dict[str, set[str]],
) -> list[str]:
    radici, unita_di = _radici_unita(componente, per_id, genitori, coniugi)
    righe: list[str] = []
    visitate: set[frozenset] = set()

    def rendi(gruppo: frozenset, livello: int, principale: str | None = None) -> None:
        if gruppo in visitate:
            return
        visitate.add(gruppo)
        righe.append("  " * livello + "- " + _nome_unita(gruppo, per_id, principale))
        for figlio in _figli_unita(gruppo, figli, unita_di, per_id):
            rendi(unita_di[figlio], livello + 1, figlio)

    for radice in radici:
        rendi(radice, 0)
    return righe


def scrivi_parentele(persone: list[dict], relazioni: list[dict]) -> None:
    dati = costruisci_parentele(persone, relazioni)
    per_id = dati["per_id"]
    collegate = dati["collegate"]
    os.makedirs(BUILD_DIR, exist_ok=True)
    persone_json = []
    for persona in persone:
        persone_json.append({
            "id": persona["id"],
            "nome": persona["nome"],
            "genere": persona.get("genere"),
            "specie": persona.get("specie"),
            "popolo": persona.get("popolo"),
            "nascita": persona.get("nascita"),
            "morte": persona.get("morte"),
            "collegata": persona["id"] in collegate,
        })
    componenti_json = []
    for membri in dati["componenti"]:
        radici, _ = _radici_unita(membri, per_id, dati["genitori"], dati["coniugi"])
        componenti_json.append({
            "membri": membri,
            "radici": sorted(
                (pid for gruppo in radici for pid in gruppo),
                key=lambda pid: per_id[pid]["nome"],
            ),
        })
    with open(os.path.join(BUILD_DIR, "relazioni.json"), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "persone": persone_json,
                "relazioni": relazioni,
                "derivate": {
                    "figli": {k: sorted(v) for k, v in sorted(dati["figli"].items())},
                    "genitori": {k: sorted(v) for k, v in sorted(dati["genitori"].items())},
                    "coniugi": {k: sorted(v) for k, v in sorted(dati["coniugi"].items())},
                    "fratelli": {k: sorted(v) for k, v in sorted(dati["fratelli"].items())},
                },
                "componenti": componenti_json,
                "copertura": {
                    "persone_totali": len(persone),
                    "persone_collegate": len(collegate),
                    "relazioni": len(relazioni),
                    "genitore": sum(1 for r in relazioni if r["tipo"] == "genitore"),
                    "coniuge": sum(1 for r in relazioni if r["tipo"] == "coniuge"),
                    "componenti": len(dati["componenti"]),
                },
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
    coppie_fratelli = sum(len(v) for v in dati["fratelli"].values()) // 2
    senza_genere = [p["nome"] for p in persone if p.get("genere") not in GENERI]
    non_collegate = sorted(
        (p for p in persone if p["id"] not in collegate),
        key=_ordine_persona,
    )
    righe = [
        "# Rapporto sulle parentele",
        "",
        f"- Relazioni registrate: **{len(relazioni)}**.",
        f"  - genitore: **{sum(1 for r in relazioni if r['tipo'] == 'genitore')}**.",
        f"  - coniuge: **{sum(1 for r in relazioni if r['tipo'] == 'coniuge')}**.",
        f"- Persone collegate: **{len(collegate)}** su **{len(persone)}**.",
        f"- Gruppi familiari (componenti): **{len(dati['componenti'])}**.",
        f"- Coppie di fratelli ricavate dai genitori comuni: **{coppie_fratelli}**.",
        f"- Persone con genere dichiarato: **{len(persone) - len(senza_genere)}**.",
        "",
        "## Controlli superati",
        "",
        "- Ogni relazione rimanda a due persone che esistono.",
        "- Nessuna persona è genitore di se stessa.",
        "- Nessun ciclo: nessuno è antenato di se stesso.",
        "- Ogni figlio ha al massimo un padre e una madre.",
        "- Nessun genitore è nato prima o nello stesso anno del figlio.",
        "- Nessuna coppia di coniugi è registrata due volte.",
        "- Ogni persona citata in una relazione ha il genere dichiarato.",
        "",
        "## Gruppi familiari",
        "",
        "| Gruppo | Membri | Radici |",
        "|---|---|---|",
    ]
    for numero, membri in enumerate(dati["componenti"], 1):
        radici, _ = _radici_unita(membri, per_id, dati["genitori"], dati["coniugi"])
        nomi = ", ".join(sorted(per_id[pid]["nome"] for pid in membri))
        nomi_radici = "; ".join(_nome_unita(g, per_id) for g in radici)
        righe.append(f"| {numero} | {nomi} | {nomi_radici or '—'} |")
    righe += [
        "",
        "## Persone collegate",
        "",
        "| Persona | Genere | Genitori | Coniugi | Figli |",
        "|---|---|---|---|---|",
    ]
    def nomi_di(ids: set[str]) -> str:
        return ", ".join(
            per_id[i]["nome"] for i in sorted(ids, key=lambda i: per_id[i]["nome"])
        ) or "—"

    for pid in sorted(collegate, key=lambda i: per_id[i]["nome"]):
        persona = per_id[pid]
        righe.append(
            f"| {persona['nome']} | {persona.get('genere') or '—'} | "
            f"{nomi_di(dati['genitori'].get(pid, set()))} | "
            f"{nomi_di(dati['coniugi'].get(pid, set()))} | "
            f"{nomi_di(dati['figli'].get(pid, set()))} |"
        )
    righe += [
        "",
        "## Limiti noti",
        "",
        "- Il pilota copre una sola casata: la Casa di Elrond. Mancano Isildur,",
        "  Rohan, Durin, i Sovrintendenti e gli Hobbit.",
        "- Una persona con più coniugi viene raggruppata in un unico nodo. Quando",
        "  servirà, i matrimoni andranno separati con un identificativo proprio.",
        "- I fratelli sono ricavati dai genitori comuni e non hanno una distinzione",
        "  tra fratelli pieni e fratellastri.",
        "",
        "## Persone non ancora collegate",
        "",
        f"Sono **{len(non_collegate)}**. Verranno aggiunte una casata alla volta.",
        "",
        "<details>",
        "<summary>Mostra l'elenco</summary>",
        "",
    ]
    for persona in non_collegate:
        righe.append(f"- {persona['nome']}")
    righe += ["", "</details>", ""]
    with open(os.path.join(BUILD_DIR, "rapporto-parentele.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(righe))
    righe_alberi = [
        "# Alberi genealogici (testo)",
        "",
        "Generato da `data/relazioni.yaml`. Il simbolo ⚭ indica un matrimonio.",
        "Le righe indentate sono i figli della coppia sopra.",
        "",
    ]
    for numero, membri in enumerate(dati["componenti"], 1):
        righe_alberi.append(f"## Gruppo {numero} ({len(membri)} persone)")
        righe_alberi.append("")
        albero = _albero_componente(
            membri, per_id, dati["figli"], dati["genitori"], dati["coniugi"]
        )
        radici = [riga[2:] for riga in albero if riga.startswith("- ")]
        if radici:
            righe_alberi.append("Radici: " + ", ".join(radici))
            righe_alberi.append("")
        righe_alberi.extend(albero)
        righe_alberi.append("")
    with open(os.path.join(BUILD_DIR, "alberi.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(righe_alberi))


def arricchisci_partecipanti(eventi: list[dict], persone: list[dict], entita: list[dict]) -> None:
    per_id = {p["id"]: p for p in persone + entita}
    for ev in eventi:
        nuovi = []
        for p in ev["partecipanti"]:
            pid = p.get("persona") or p.get("entita")
            voce = per_id[pid]
            nuovo = {
                "nome": voce["nome"],
                "id": pid,
                "tipo": voce["tipo"],
                "parte": p.get("parte"),
                "ruolo": p.get("ruolo"),
                "esito": p.get("esito"),
            }
            nuovi.append(nuovo)
        ev["partecipanti"] = nuovi


def indice_nomi_entita(entita: list[dict]) -> dict[str, str]:
    indice: dict[str, str] = {}
    for voce in entita:
        indice[voce["nome"]] = voce["id"]
        for nome_alias in voce.get("alias") or []:
            indice[nome_alias] = voce["id"]
    return indice


def collega_entita(eventi: list[dict], entita: list[dict]) -> dict:
    indice = indice_nomi_entita(entita)
    citazioni: dict[str, list[str]] = {}
    for ev in eventi:
        for partecipante in ev["partecipanti"]:
            nome = partecipante["nome"]
            citazioni.setdefault(nome, []).append(ev["id"])
    coperti = {nome: indice[nome] for nome in citazioni if nome in indice}
    scoperti = {nome: ids for nome, ids in citazioni.items() if nome not in indice}
    per_entita: dict[str, set[str]] = {}
    for nome, eid in coperti.items():
        per_entita.setdefault(eid, set()).update(citazioni[nome])
    schede = []
    for voce in entita:
        record = dict(voce)
        record["eventi"] = sorted(per_entita.get(voce["id"], set()))
        schede.append(record)
    return {
        "schede": schede,
        "coperti": coperti,
        "scoperti": scoperti,
        "per_entita": {k: sorted(v) for k, v in per_entita.items()},
    }


DI_MESI = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]


def giorno_dell_anno(mese: int, giorno: int) -> int:
    return DI_MESI[mese - 1] + giorno


def anno_decimale(d: dict) -> float:
    """Posizione sul cerchio: un decimale come nel dataset originale."""
    anno = d["anno"]
    mese, giorno = d.get("mese"), d.get("giorno")
    if mese and giorno:
        return round(anno + (giorno_dell_anno(mese, giorno) - 1) / 365, 2)
    if mese:
        return round(anno + (giorno_dell_anno(mese, 15) - 1) / 365, 2)
    return float(anno)


def scrivi_js(eventi: list[dict], luoghi: list[dict]) -> None:
    nomi_luoghi = {l["id"]: l["nome"] for l in luoghi}
    eras = [
        {"id": "lampade", "name": "Era delle Lampadi", "len": None, "scale": False, "active": False},
        {"id": "alberi", "name": "Era degli Alberi", "len": None, "scale": False, "active": False},
        {"id": "prima", "name": "Prima Era", "len": 590, "scale": True, "active": False},
        {"id": "seconda", "name": "Seconda Era", "len": 3441, "scale": True, "active": False},
        {"id": "terza", "name": "Terza Era", "len": 3021, "scale": True, "active": True},
        {"id": "quarta", "name": "Quarta Era", "len": None, "scale": False, "active": False},
    ]
    righe = [
        "/* File generato da tools/build_data.py. Non modificare a mano.",
        "   Fonte: data/eventi/*.yaml. */",
        "",
        "const ERAS=" + json.dumps(eras, ensure_ascii=False, indent=2) + ";",
        "",
        "const EVENTS=[",
    ]
    for ev in sorted(eventi, key=lambda e: (anno_decimale(e["data"]), e["id"])):
        d = ev["data"]
        nomi = [nomi_luoghi[lid] for lid in ev["luoghi"]]
        record = {
            "id": ev["id"],
            "era": d["era"],
            "year": anno_decimale(d),
            "approx": d.get("qualificatore") == "circa",
            "label": d["testo"],
            "title": ev["titolo"],
            "desc": ev["breve"],
            "type": ev["tipo"],
            "place": nomi[0],
            "people": [p["nome"] for p in ev["partecipanti"]],
            "source": ev["fonti"][0]["riferimento"],
            "short": ev["breve"],
            "long": ev["lungo"],
            "places": nomi,
            "place_ids": ev["luoghi"],
            "participants": ev["partecipanti"],
            "sources": ev["fonti"],
            "certainty": ev["certezza"],
            "parent": ev.get("fa_parte_di"),
            "note": ev.get("note"),
        }
        righe.append("  " + json.dumps(record, ensure_ascii=False) + ",")
    righe += ["];", ""]
    os.makedirs(JS_DIR, exist_ok=True)
    with open(os.path.join(JS_DIR, "data.js"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(righe))


def scrivi_sqlite(eventi: list[dict], luoghi: list[dict]) -> None:
    nomi_luoghi = {l["id"]: l["nome"] for l in luoghi}
    os.makedirs(BUILD_DIR, exist_ok=True)
    path = os.path.join(BUILD_DIR, "arda.sqlite")
    if os.path.exists(path):
        os.remove(path)
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE events (
            id TEXT PRIMARY KEY, title TEXT, type TEXT, era TEXT,
            year INTEGER, month INTEGER, day INTEGER, year_end INTEGER,
            precision TEXT, qualifier TEXT, calendar TEXT, display TEXT,
            short TEXT, long TEXT, certainty TEXT, parent TEXT, note TEXT
        );
        CREATE TABLE participants (
            event_id TEXT, name TEXT, side TEXT, role TEXT, outcome TEXT
        );
        CREATE TABLE places (event_id TEXT, place_id TEXT, name TEXT);
        CREATE TABLE sources (event_id TEXT, work TEXT, reference TEXT);
        """
    )
    for ev in eventi:
        d = ev["data"]
        cur.execute(
            "INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (ev["id"], ev["titolo"], ev["tipo"], d["era"], d["anno"], d.get("mese"),
             d.get("giorno"), d.get("anno_fine"), d["precisione"], d.get("qualificatore"),
             d["calendario"], d["testo"], ev["breve"], ev["lungo"], ev["certezza"],
             ev.get("fa_parte_di"), ev.get("note")),
        )
        for p in ev["partecipanti"]:
            cur.execute("INSERT INTO participants VALUES (?,?,?,?,?)",
                        (ev["id"], p["nome"], p.get("parte"), p.get("ruolo"), p.get("esito")))
        for lid in ev["luoghi"]:
            cur.execute("INSERT INTO places VALUES (?,?,?)",
                        (ev["id"], lid, nomi_luoghi[lid]))
        for f in ev["fonti"]:
            cur.execute("INSERT INTO sources VALUES (?,?,?)", (ev["id"], f["opera"], f["riferimento"]))
    con.commit()
    con.close()


def scrivi_indici(eventi: list[dict], luoghi: list[dict]) -> None:
    nomi_luoghi = {l["id"]: l["nome"] for l in luoghi}
    per_tipo: dict[str, list[str]] = {}
    per_anno: dict[int, list[str]] = {}
    per_persona: dict[str, list[str]] = {}
    per_luogo: dict[str, list[str]] = {}
    per_luogo_id: dict[str, list[str]] = {}
    for ev in eventi:
        per_tipo.setdefault(ev["tipo"], []).append(ev["id"])
        per_anno.setdefault(ev["data"]["anno"], []).append(ev["id"])
        for p in ev["partecipanti"]:
            per_persona.setdefault(p["nome"], []).append(ev["id"])
        for lid in ev["luoghi"]:
            per_luogo.setdefault(nomi_luoghi[lid], []).append(ev["id"])
            per_luogo_id.setdefault(lid, []).append(ev["id"])
    indici = {
        "per_tipo": per_tipo,
        "per_anno": {str(k): v for k, v in sorted(per_anno.items())},
        "per_persona": dict(sorted(per_persona.items())),
        "per_luogo": dict(sorted(per_luogo.items())),
        "per_luogo_id": dict(sorted(per_luogo_id.items())),
    }
    os.makedirs(BUILD_DIR, exist_ok=True)
    with open(os.path.join(BUILD_DIR, "indexes.json"), "w", encoding="utf-8") as fh:
        json.dump(indici, fh, ensure_ascii=False, indent=2)


def scrivi_schede(eventi: list[dict], luoghi: list[dict]) -> None:
    nomi_luoghi = {l["id"]: l["nome"] for l in luoghi}
    righe = ["# Schede della Terza Era", "",
             "Generate da `data/eventi/*.yaml`. Ogni scheda è la versione lunga;",
             "la versione breve è quella che compare sulla linea del tempo.", ""]
    for ev in sorted(eventi, key=lambda e: (anno_decimale(e["data"]), e["id"])):
        d = ev["data"]
        righe.append(f"## {ev['titolo']}")
        righe.append("")
        righe.append(f"**ID:** `{ev['id']}` · **Tipo:** {ev['tipo']} · **Certezza:** {ev['certezza']}")
        righe.append("")
        righe.append(f"**Quando:** {d['testo']} · {NOMI_ERA.get(d['era'], d['era'])}")
        righe.append("")
        righe.append(f"**Dove:** {', '.join(nomi_luoghi[lid] for lid in ev['luoghi'])}")
        righe.append("")
        if ev.get("fa_parte_di"):
            righe.append(f"**Fa parte di:** {ev['fa_parte_di']}")
            righe.append("")
        righe.append("**Partecipanti:**")
        righe.append("")
        righe.append("| Nome | Parte | Ruolo | Esito |")
        righe.append("|---|---|---|---|")
        for p in ev["partecipanti"]:
            righe.append(f"| {p['nome']} | {p.get('parte') or '—'} | {p.get('ruolo') or '—'} | {p.get('esito') or '—'} |")
        righe.append("")
        righe.append(f"**Versione breve:** {ev['breve']}")
        righe.append("")
        righe.append(f"**Testo lungo:** {ev['lungo']}")
        righe.append("")
        righe.append("**Fonti:**")
        for f in ev["fonti"]:
            righe.append(f"- {f['opera']}, {f['riferimento']}")
        righe.append("")
        if ev.get("note"):
            righe.append(f"**Note:** {ev['note']}")
            righe.append("")
    with open(os.path.join(BUILD_DIR, "schede-terza-era.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(righe))


def scrivi_rapporto(eventi: list[dict], luoghi: list[dict]) -> None:
    nomi_luoghi = {l["id"]: l["nome"] for l in luoghi}
    ids = {e["id"] for e in eventi}
    nuovi = sorted(ids - ID_ORIGINALI)
    mancanti = sorted(ID_ORIGINALI - ids)
    solo_anno = [e for e in eventi if e["data"]["precisione"] in ("anno", "ignoto")]
    incerti = [e for e in eventi if e["certezza"] != "certa" or e.get("note")]
    persone = {}
    luoghi = {}
    for e in eventi:
        for p in e["partecipanti"]:
            persone[p["nome"]] = persone.get(p["nome"], 0) + 1
        for lid in e["luoghi"]:
            nome = nomi_luoghi[lid]
            luoghi[nome] = luoghi.get(nome, 0) + 1
    righe = [
        "# Rapporto sul lavoro — Terza Era",
        "",
        f"- Eventi: **{len(eventi)}** (erano {len(ID_ORIGINALI)}).",
        f"- Partecipanti nominati: **{len(persone)}** nomi distinti, {sum(persone.values())} presenze.",
        f"- Luoghi nominati: **{len(luoghi)}** nomi distinti.",
        f"- Eventi con solo anno (o senza anno): **{len(solo_anno)}**.",
        f"- Eventi con nota o certezza non piena: **{len(incerti)}**.",
        "",
        "## Eventi separati",
        "",
        "Alcuni eventi del dataset originale contenevano più avvenimenti distinti.",
        "Sono stati separati perché hanno partecipanti e conseguenze diverse.",
        "",
    ]
    for padre, figli in SEPARAZIONI.items():
        presenti = [f for f in figli if f in ids]
        if presenti:
            righe.append(f"- `{padre}` → " + ", ".join(f"`{f}`" for f in presenti))
    righe += ["", "## Eventi aggiunti", ""]
    for eid in sorted(AGGIUNTI & ids):
        ev = next(e for e in eventi if e["id"] == eid)
        righe.append(f"- `{eid}` — {ev['titolo']}")
    righe += ["", "## Correzioni di nome", ""]
    for prima, dopo, motivo in CORREZIONI:
        righe.append(f"- **{prima} → {dopo}**: {motivo}.")
    righe += ["", "## Casi da sapere", ""]
    for e in incerti:
        if e.get("note"):
            righe.append(f"- **{e['titolo']}** (`{e['id']}`): {e['note']}")
    righe += [
        "",
        "## Cosa manca ancora",
        "",
        "- I partecipanti sono collegati agli eventi tramite ID; le schede persona",
        "  ed entità collettiva sono pronte. Le parentele sono cominciate con la",
        "  Casa di Elrond (`data/relazioni.yaml`); mancano le altre casate e le fonti",
        "  come entità separate.",
        "- I luoghi sono ora collegati agli eventi tramite ID: la fase mappa assegnerà",
        "  coordinate e scene (Arda piatta / Arda rotonda).",
        "- Gli eventi del 2941 e del 3019 sono stati separati, ma restano da aggiungere",
        "  gli altri fatti dell'Appendice B (battaglie del Nord, assalti a Lórien,",
        "  distruzione di Dol Guldur, Campo di Cormallen).",
        "- Le date con solo l'anno non hanno giorno e mese: è voluto, non è una lacuna",
        "  del lavoro. Il sito deve mostrarle come «anno» e non inventare precisione.",
        "",
    ]
    with open(os.path.join(BUILD_DIR, "rapporto.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(righe))


def scrivi_luoghi(eventi: list[dict], luoghi: list[dict]) -> None:
    dati = collega_luoghi(eventi, luoghi)
    os.makedirs(BUILD_DIR, exist_ok=True)
    citati = len(dati["citati"])
    with open(os.path.join(BUILD_DIR, "luoghi.json"), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "luoghi": dati["schede"],
                "copertura": {
                    "luoghi_citati": citati,
                    "luoghi_coperti": citati - len(dati["scoperti"]),
                    "luoghi_scoperti": len(dati["scoperti"]),
                    "scoperti": sorted(dati["scoperti"]),
                },
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
    righe = [
        "# Rapporto sui luoghi",
        "",
        f"- Schede create: **{len(luoghi)}**.",
        f"- Luoghi citati dagli eventi: **{citati}** distinti "
        f"(su {sum(len(e['luoghi']) for e in eventi)} citazioni).",
        f"- Luoghi con una scheda: **{citati - len(dati['scoperti'])}**.",
        f"- Luoghi senza scheda: **{len(dati['scoperti'])}**.",
        "",
        "## Schede",
        "",
        "| ID | Nome | Tipo | Dentro | Eventi collegati |",
        "|---|---|---|---|---|",
    ]
    for luogo in dati["schede"]:
        righe.append(
            f"| `{luogo['id']}` | {luogo['nome']} | {luogo['tipo']} | "
            f"{luogo.get('dentro') or '—'} | {len(luogo['eventi'])} |"
        )
    if dati["scoperti"]:
        righe += [
            "",
            "## Nomi citati dagli eventi, non ancora coperti",
            "",
            "Questi nomi aspettano il prossimo blocco. Alcuni sono doppioni o varianti",
            "di luoghi già presenti: vanno uniti con un alias, non duplicati.",
            "",
        ]
        for nome in sorted(dati["scoperti"]):
            righe.append(f"- {nome}")
    else:
        righe += [
            "",
            "## Copertura",
            "",
            "Tutti i nomi di luogo citati dagli eventi hanno una scheda.",
        ]
    righe.append("")
    with open(os.path.join(BUILD_DIR, "rapporto-luoghi.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(righe))


def scrivi_persone(eventi: list[dict], persone: list[dict], entita: list[dict]) -> None:
    dati = collega_persone(eventi, persone)
    indice_entita = indice_nomi_entita(entita)
    coperti_da_entita = {n: indice_entita[n] for n in dati["scoperti"] if n in indice_entita}
    mancanti = {n: ids for n, ids in dati["scoperti"].items() if n not in indice_entita}
    os.makedirs(BUILD_DIR, exist_ok=True)
    nomi_citati = len(dati["coperti"]) + len(dati["scoperti"])
    with open(os.path.join(BUILD_DIR, "persone.json"), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "persone": dati["schede"],
                "copertura": {
                    "nomi_citati": nomi_citati,
                    "nomi_coperti": len(dati["coperti"]),
                    "nomi_coperti_da_entita": len(coperti_da_entita),
                    "nomi_scoperti": len(mancanti),
                    "scoperti": dict(sorted(mancanti.items())),
                },
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
    righe = [
        "# Rapporto sulle persone",
        "",
        f"- Schede create: **{len(persone)}**.",
        f"- Nomi di partecipante citati dagli eventi: **{nomi_citati}** distinti.",
        f"- Nomi coperti da una scheda persona: **{len(dati['coperti'])}**.",
        f"- Nomi coperti da un'entità collettiva: **{len(coperti_da_entita)}**.",
        f"- Nomi ancora senza scheda: **{len(mancanti)}**.",
        "",
        "## Schede",
        "",
        "| ID | Nome | Tipo | Specie | Genere | Eventi collegati |",
        "|---|---|---|---|---|---|",
    ]
    for persona in dati["schede"]:
        righe.append(
            f"| `{persona['id']}` | {persona['nome']} | {persona['tipo']} | "
            f"{persona.get('specie') or '—'} | {persona.get('genere') or '—'} | {len(persona['eventi'])} |"
        )
    righe += [
        "",
        "## Nomi di partecipante non ancora coperti",
        "",
    ]
    if mancanti:
        for nome in sorted(mancanti):
            righe.append(f"- {nome}")
    else:
        righe.append("Nessuno: tutti i nomi hanno una scheda persona o un'entità collettiva.")
    righe.append("")
    with open(os.path.join(BUILD_DIR, "rapporto-persone.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(righe))


def scrivi_entita(eventi: list[dict], entita: list[dict]) -> None:
    dati = collega_entita(eventi, entita)
    os.makedirs(BUILD_DIR, exist_ok=True)
    with open(os.path.join(BUILD_DIR, "entita.json"), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "entita": dati["schede"],
                "copertura": {
                    "nomi_coperti": len(dati["coperti"]),
                    "nomi_scoperti": len(dati["scoperti"]),
                },
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
    righe = [
        "# Rapporto sulle entità collettive",
        "",
        f"- Schede create: **{len(entita)}**.",
        f"- Nomi di partecipante coperti: **{len(dati['coperti'])}**.",
        "",
        "## Schede",
        "",
        "| ID | Nome | Tipo | Eventi collegati |",
        "|---|---|---|---|",
    ]
    for voce in dati["schede"]:
        righe.append(
            f"| `{voce['id']}` | {voce['nome']} | {voce['tipo']} | {len(voce['eventi'])} |"
        )
    righe.append("")
    with open(os.path.join(BUILD_DIR, "rapporto-entita.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(righe))


def scrivi_partecipanti(eventi: list[dict], persone: list[dict], entita: list[dict]) -> None:
    indice = {}
    tipo_di = {}
    for voce in persone + entita:
        tipo_di[voce["id"]] = voce["tipo"]
        for chiave in [voce["nome"]] + (voce.get("alias") or []):
            indice[chiave] = voce["id"]
    citati = {}
    for ev in eventi:
        for partecipante in ev["partecipanti"]:
            citati.setdefault(partecipante["nome"], set()).add(ev["id"])
    coperti = {n: indice[n] for n in citati if n in indice}
    mancanti = sorted(n for n in citati if n not in indice)
    per_tipo = {}
    for nome, pid in coperti.items():
        per_tipo[tipo_di[pid]] = per_tipo.get(tipo_di[pid], 0) + 1
    righe = [
        "# Rapporto sui partecipanti",
        "",
        f"- Nomi di partecipante citati: **{len(citati)}**.",
        f"- Nomi con una scheda: **{len(coperti)}**.",
        f"- Nomi senza scheda: **{len(mancanti)}**.",
        "",
        "## Per tipo",
        "",
        "| Tipo | Nomi coperti |",
        "|---|---|",
    ]
    for tipo in ("personaggio", "popolo", "regno", "gruppo"):
        righe.append(f"| {tipo} | {per_tipo.get(tipo, 0)} |")
    righe.append("")
    if mancanti:
        righe += ["## Nomi senza scheda", ""]
        for nome in mancanti:
            righe.append(f"- {nome}")
        righe.append("")
    with open(os.path.join(BUILD_DIR, "rapporto-partecipanti.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(righe))


def scrivi_audit(
    eventi: list[dict],
    luoghi: list[dict],
    persone: list[dict],
    entita: list[dict],
    relazioni: list[dict],
) -> None:
    usati_partecipanti = set()
    usati_luoghi = set()
    parti = Counter()
    ruoli = Counter()
    esiti = Counter()
    for ev in eventi:
        usati_luoghi.update(ev["luoghi"])
        for p in ev["partecipanti"]:
            usati_partecipanti.add(p["id"])
            parti[p.get("parte")] += 1
            ruoli[p.get("ruolo")] += 1
            esiti[p.get("esito")] += 1
    senza_eventi_persone = [v["nome"] for v in persone if v["id"] not in usati_partecipanti]
    senza_eventi_entita = [v["nome"] for v in entita if v["id"] not in usati_partecipanti]
    senza_eventi_luoghi = [v["nome"] for v in luoghi if v["id"] not in usati_luoghi]
    generiche = {"Montagne", "Nord", "Est", "invasori", "ribelli", "Gondor e Rohan", "Eldar e Istari"}
    parentele = costruisci_parentele(persone, relazioni)
    righe = [
        "# Controllo del database",
        "",
        f"- Eventi: **{len(eventi)}**.",
        f"- Luoghi: **{len(luoghi)}**.",
        f"- Personaggi: **{len(persone)}**.",
        f"- Entità collettive: **{len(entita)}**.",
        f"- Partecipanti: **{sum(len(e['partecipanti']) for e in eventi)}**.",
        f"- Citazioni di luogo: **{sum(len(e['luoghi']) for e in eventi)}**.",
        "",
        "## Coerenza",
        "",
        f"- Partecipanti senza scheda: **0**.",
        f"- Luoghi senza scheda: **0**.",
        f"- Personaggi senza eventi: **{len(senza_eventi_persone)}**.",
        f"- Entità senza eventi: **{len(senza_eventi_entita)}**.",
        f"- Luoghi senza eventi: **{len(senza_eventi_luoghi)}**.",
        "",
        "## Vocabolario",
        "",
        f"- Parti distinte: **{len(parti)}**.",
        f"- Ruoli distinti: **{len(ruoli)}**.",
        f"- Esiti distinti: **{len(esiti)}**.",
        "",
        "### Parti generiche",
        "",
        "Sono etichette volutamente ampie, usate quando la fonte non specifica il",
        "contesto. Non sono errori, ma non sono filtri precisi.",
        "",
    ]
    for parte in sorted(generiche):
        if parti[parte]:
            righe.append(f"- {parte}: {parti[parte]}")
    righe += [
        "",
        "## Parentele",
        "",
        f"- Relazioni registrate: **{len(relazioni)}**.",
        f"- Persone collegate: **{len(parentele['collegate'])}** su **{len(persone)}**.",
        f"- Gruppi familiari: **{len(parentele['componenti'])}**.",
        f"- Persone con genere dichiarato: **{sum(1 for p in persone if p.get('genere') in GENERI)}**.",
        "",
    ]
    if senza_eventi_persone or senza_eventi_entita or senza_eventi_luoghi:
        righe += ["", "## Schede non collegate", ""]
        for nome in senza_eventi_persone:
            righe.append(f"- personaggio: {nome}")
        for nome in senza_eventi_entita:
            righe.append(f"- entità: {nome}")
        for nome in senza_eventi_luoghi:
            righe.append(f"- luogo: {nome}")
    righe.append("")
    with open(os.path.join(BUILD_DIR, "rapporto-dati.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(righe))


def main() -> None:
    eventi = carica()
    valida(eventi)
    luoghi = carica_luoghi()
    valida_luoghi(luoghi)
    valida_riferimenti_luoghi(eventi, luoghi)
    persone = carica_persone()
    valida_persone(persone)
    entita = carica_entita()
    valida_entita(entita)
    valida_nomi_unici(persone, entita)
    relazioni = carica_relazioni()
    valida_relazioni(relazioni, persone)
    valida_riferimenti_partecipanti(eventi, persone, entita)
    arricchisci_partecipanti(eventi, persone, entita)
    scrivi_js(eventi, luoghi)
    scrivi_sqlite(eventi, luoghi)
    scrivi_indici(eventi, luoghi)
    scrivi_schede(eventi, luoghi)
    scrivi_rapporto(eventi, luoghi)
    scrivi_luoghi(eventi, luoghi)
    scrivi_persone(eventi, persone, entita)
    scrivi_entita(eventi, entita)
    scrivi_partecipanti(eventi, persone, entita)
    scrivi_audit(eventi, luoghi, persone, entita, relazioni)
    scrivi_parentele(persone, relazioni)
    print(f"OK: {len(eventi)} eventi, {len(luoghi)} luoghi, {len(persone)} persone e {len(entita)} entità compilati.")
    print(f"  js/data.js")
    print(f"  build/arda.sqlite")
    print(f"  build/indexes.json")
    print(f"  build/luoghi.json")
    print(f"  build/persone.json")
    print(f"  build/entita.json")
    print(f"  build/schede-terza-era.md")
    print(f"  build/rapporto.md")
    print(f"  build/rapporto-luoghi.md")
    print(f"  build/rapporto-persone.md")
    print(f"  build/rapporto-entita.md")
    print(f"  build/rapporto-partecipanti.md")
    print(f"  build/rapporto-dati.md")
    print(f"  build/relazioni.json")
    print(f"  build/rapporto-parentele.md")
    print(f"  build/alberi.md")


if __name__ == "__main__":
    main()
