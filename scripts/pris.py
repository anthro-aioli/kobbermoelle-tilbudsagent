#!/usr/bin/env python3
"""Deterministisk prisberegner for Kobbermølle Fragt ApS."""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
UDSTEDT = date(2026, 10, 1)


def paaske(aar):
    """Beregn påskedag efter den gregorianske kalender."""
    a = aar % 19
    b = aar // 100
    c = aar % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    maaned = (h + l - 7 * m + 114) // 31
    dag = (h + l - 7 * m + 114) % 31 + 1
    return date(aar, maaned, dag)


def helligdage(aar):
    paaskedag = paaske(aar)
    return {
        date(aar, 1, 1): "nytårsdag",
        paaskedag - timedelta(days=3): "skærtorsdag",
        paaskedag - timedelta(days=2): "langfredag",
        paaskedag: "påskedag",
        paaskedag + timedelta(days=1): "2. påskedag",
        paaskedag + timedelta(days=39): "Kristi himmelfartsdag",
        paaskedag + timedelta(days=49): "pinsedag",
        paaskedag + timedelta(days=50): "2. pinsedag",
        date(aar, 12, 25): "juledag",
        date(aar, 12, 26): "2. juledag",
    }


def zone_og_pris(land, postnr):
    nummer = int(postnr)
    if land == "DK":
        return ("DK Syd", 450) if 6000 <= nummer <= 6999 else ("DK Øvrig", 650)
    if land == "DE":
        return ("DE Nord", 500) if 20000 <= nummer <= 25999 else ("DE Øvrig", 800)
    raise ValueError("Leveringslandet skal være DK eller DE")


def hent_json(sti):
    with sti.open(encoding="utf-8") as fil:
        return json.load(fil)


def vis_tal(tal):
    return int(tal) if float(tal).is_integer() else round(tal, 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--postnr", required=True)
    parser.add_argument("--land", choices=("DK", "DE"), required=True)
    parser.add_argument("--paller", type=int, required=True)
    parser.add_argument("--vaegt", type=float, required=True)
    parser.add_argument("--dato", type=date.fromisoformat, required=True)
    parser.add_argument("--kunde")
    parser.add_argument("--kundeland", choices=("DK", "DE"), default="DK")
    args = parser.parse_args()

    if args.paller <= 0 or args.vaegt < 0:
        parser.error("paller skal være positivt og vægt må ikke være negativ")

    kunder = hent_json(ROOT / "data" / "kunder.json")
    kunde = None
    if args.kunde:
        kunde = next((element for element in kunder if element["id"] == args.kunde), None)
        if kunde is None:
            parser.error(f"ukendt kunde: {args.kunde}")
        if kunde["kreditspærret"]:
            print(json.dumps({"stop": "kreditspærret"}, ensure_ascii=False))
            return 2

    zone, zonepris = zone_og_pris(args.land, args.postnr)
    gennemsnit = args.vaegt / args.paller
    pladser = args.paller * (2 if gennemsnit > 700 else 1)
    saerpris = kunde["særaftale_pris_pr_plads"] if kunde else None
    pris_pr_plads = saerpris if saerpris is not None else zonepris
    prisgrundlag = "særaftale" if saerpris is not None else "zone"
    grundbeloeb = pladser * pris_pr_plads

    fridage = helligdage(args.dato.year)
    if args.dato in fridage:
        tillaeg_grund = fridage[args.dato]
    elif args.dato.weekday() == 5:
        tillaeg_grund = "lørdag"
    elif args.dato.weekday() == 6:
        tillaeg_grund = "søndag"
    else:
        tillaeg_grund = None
    tillaeg = grundbeloeb * 0.25 if tillaeg_grund else 0
    total = grundbeloeb + tillaeg

    resultat = {
        "kunde": kunde["id"] if kunde else "ny kunde",
        "zone": zone,
        "gennemsnit_kg_pr_palle": vis_tal(gennemsnit),
        "pladser": pladser,
        "pris_pr_plads": pris_pr_plads,
        "prisgrundlag": prisgrundlag,
        "grundbeløb": vis_tal(grundbeloeb),
        "tillæg": vis_tal(tillaeg),
        "tillæg_grund": tillaeg_grund,
        "total_dkk": vis_tal(total),
        "udstedt": UDSTEDT.isoformat(),
        "gyldig_til": (UDSTEDT + timedelta(days=14)).isoformat(),
    }

    kundeland = kunde["land"] if kunde else args.kundeland
    if kundeland == "DE":
        kurs = hent_json(ROOT / "data" / "kurs.json")
        resultat.update(
            total_eur=round(total / kurs["kurs"], 2),
            kurs=kurs["kurs"],
            kursdato=kurs["dato"],
            kilde=kurs["kilde"],
        )

    print(json.dumps(resultat, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
