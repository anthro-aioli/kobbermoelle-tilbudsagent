#!/usr/bin/env python3
"""Beregner prisen på en fragtopgave for Kobbermølle Fragt ApS.

Dækker regel 1 (zone og pladser), 2 (weekend og helligdag), 5 (gyldighed),
6 (kreditspærring) og 7 (særaftale). Regel 3, 4 og 8 afgør agenten selv,
før den kalder scriptet.

Eksempel:
    python3 scripts/pris.py --postnr 6430 --land DK --paller 2 --vaegt 900 \
        --dato 2026-10-06 --kunde K1

Skriver resultatet som JSON. Er kunden kreditspærret, nægter scriptet at
regne en pris og slutter med kode 2.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

UDSTEDT = dt.date(2026, 10, 1)
GYLDIG_DAGE = 14
MAKS_KG_PR_PALLE = 700
WEEKEND_TILLAEG = 0.25

ZONER = [
    # (land, fra postnr, til postnr, zone, pris pr. plads)
    ("DK", 6000, 6999, "DK Syd", 450),
    ("DK", 0, 99999, "DK Øvrig", 650),
    ("DE", 20000, 25999, "DE Nord", 500),
    ("DE", 0, 99999, "DE Øvrig", 800),
]

KUNDER_FIL = Path(__file__).resolve().parent.parent / "data" / "kunder.json"


def paaskedag(aar: int) -> dt.date:
    """Påskedag efter den gregorianske regel (Meeus/Jones/Butcher)."""
    a = aar % 19
    b, c = divmod(aar, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    maaned, dag = divmod(h + l - 7 * m + 114, 31)
    return dt.date(aar, maaned, dag + 1)


def danske_helligdage(aar: int) -> dict:
    p = paaskedag(aar)
    return {
        dt.date(aar, 1, 1): "nytårsdag",
        p - dt.timedelta(days=3): "skærtorsdag",
        p - dt.timedelta(days=2): "langfredag",
        p: "påskedag",
        p + dt.timedelta(days=1): "2. påskedag",
        p + dt.timedelta(days=39): "Kristi himmelfartsdag",
        p + dt.timedelta(days=49): "pinsedag",
        p + dt.timedelta(days=50): "2. pinsedag",
        dt.date(aar, 12, 25): "juledag",
        dt.date(aar, 12, 26): "2. juledag",
    }


def find_zone(land: str, postnr: int):
    for z_land, fra, til, navn, pris in ZONER:
        if z_land == land and fra <= postnr <= til:
            return navn, pris
    return None, None


def find_kunde(kunde_id: str):
    kunder = json.loads(KUNDER_FIL.read_text(encoding="utf-8"))
    for k in kunder:
        if k["id"] == kunde_id:
            return k
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Pris på en fragtopgave (Kobbermølle Fragt)")
    ap.add_argument("--postnr", required=True, help="leveringsadressens postnummer")
    ap.add_argument("--land", required=True, choices=["DK", "DE"])
    ap.add_argument("--paller", required=True, type=int)
    ap.add_argument("--vaegt", required=True, type=float, help="samlet vægt i kg")
    ap.add_argument("--dato", required=True, help="afhentnings- eller leveringsdato, ÅÅÅÅ-MM-DD")
    ap.add_argument("--kunde", help="kunde-id fra data/kunder.json (udelades for nye kunder)")
    a = ap.parse_args()

    if a.paller < 1 or a.vaegt <= 0:
        print(json.dumps({"fejl": "antal paller og vægt skal være positive tal"}, ensure_ascii=False))
        return 1

    kunde = find_kunde(a.kunde) if a.kunde else None
    if a.kunde and kunde is None:
        print(json.dumps({"fejl": f"kunde {a.kunde} findes ikke i data/kunder.json"}, ensure_ascii=False))
        return 1
    if kunde and kunde.get("kreditspærret"):
        print(json.dumps({
            "stop": "kreditspærret",
            "kunde": kunde["navn"],
            "besked": "Ingen pris. Regel 6: sagen går til bogholderiet.",
        }, ensure_ascii=False))
        return 2

    zone, zonepris = find_zone(a.land, int(a.postnr))
    dato = dt.date.fromisoformat(a.dato)
    snit = a.vaegt / a.paller
    pladser = a.paller * (2 if snit > MAKS_KG_PR_PALLE else 1)

    saerpris = kunde.get("særaftale_pris_pr_plads") if kunde else None
    pris_pr_plads = saerpris if saerpris else zonepris
    grundlag = "særaftale" if saerpris else "zone"
    grund = pladser * pris_pr_plads

    helligdag = danske_helligdage(dato.year).get(dato)
    if dato.weekday() >= 5 or helligdag:
        tillaeg_grund = helligdag or ("lørdag" if dato.weekday() == 5 else "søndag")
        tillaeg = round(grund * WEEKEND_TILLAEG, 2)
        if tillaeg == int(tillaeg):
            tillaeg = int(tillaeg)
    else:
        tillaeg_grund, tillaeg = None, 0

    print(json.dumps({
        "kunde": kunde["navn"] if kunde else "ny kunde",
        "zone": zone,
        "gennemsnit_kg_pr_palle": round(snit, 1),
        "pladser": pladser,
        "pris_pr_plads": pris_pr_plads,
        "prisgrundlag": grundlag,
        "grundbeløb": grund,
        "tillæg": tillaeg,
        "tillæg_grund": tillaeg_grund,
        "total_dkk": grund + tillaeg,
        "udstedt": UDSTEDT.isoformat(),
        "gyldig_til": (UDSTEDT + dt.timedelta(days=GYLDIG_DAGE)).isoformat(),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
