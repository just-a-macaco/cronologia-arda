#!/usr/bin/env python3
"""Compila le schede degli eventi in dati per il sito.

Legge i file YAML in data/eventi/ e data/luoghi.yaml, controlla i riferimenti e produce:
  - js/data.js                 (formato compatibile con js/circle.js)
  - build/arda.sqlite          (database interrogabile con SQL)
  - build/indexes.json         (indici per ricerca e filtri)
  - build/luoghi.json          (anagrafica dei luoghi e copertura degli eventi)
  - build/schede-terza-era.md  (le schede in forma leggibile)
  - build/rapporto.md          (riepilogo del lavoro)
  - build/rapporto-luoghi.md   (stato dell'anagrafica dei luoghi)

Uso: python3 tools/build_data.py
"""
from __future__ import annotations

import glob
import json
import os
import sqlite3
import sys
from datetime import date

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "eventi")
LUOGHI_FILE = os.path.join(ROOT, "data", "luoghi.yaml")
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
            if not p.get("nome"):
                fail(f"{eid}: partecipante senza nome")
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
        "- I partecipanti sono nomi, non ancora schede persona collegate: la fase alberi",
        "  li trasformerà in entità con ID, parentele e relazioni.",
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


def main() -> None:
    eventi = carica()
    valida(eventi)
    luoghi = carica_luoghi()
    valida_luoghi(luoghi)
    valida_riferimenti_luoghi(eventi, luoghi)
    scrivi_js(eventi, luoghi)
    scrivi_sqlite(eventi, luoghi)
    scrivi_indici(eventi, luoghi)
    scrivi_schede(eventi, luoghi)
    scrivi_rapporto(eventi, luoghi)
    scrivi_luoghi(eventi, luoghi)
    print(f"OK: {len(eventi)} eventi e {len(luoghi)} luoghi compilati.")
    print(f"  js/data.js")
    print(f"  build/arda.sqlite")
    print(f"  build/indexes.json")
    print(f"  build/luoghi.json")
    print(f"  build/schede-terza-era.md")
    print(f"  build/rapporto.md")
    print(f"  build/rapporto-luoghi.md")


if __name__ == "__main__":
    main()
