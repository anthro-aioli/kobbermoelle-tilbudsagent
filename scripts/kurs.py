#!/usr/bin/env python3
"""Henter dagens EUR/DKK-referencekurs fra Den Europæiske Centralbank (ECB).

Eksempel:
    python3 scripts/kurs.py --dkk 5000

Kan ECB ikke nås, bruger scriptet reservekursen i data/kurs.json og siger
det i feltet "hentet". Skriv altid kurs, kursdato og kilde i tilbuddet.
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

ECB_URL = ("https://data-api.ecb.europa.eu/service/data/EXR/"
           "D.DKK.EUR.SP00.A?lastNObservations=1&format=csvdata")
RESERVE = Path(__file__).resolve().parent.parent / "data" / "kurs.json"


def hent_ecb():
    req = urllib.request.Request(ECB_URL, headers={"Accept": "text/csv"})
    tekst = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
    linjer = tekst.strip().splitlines()
    felter = dict(zip(linjer[0].split(","), linjer[1].split(",")))
    return {
        "kurs": float(felter["OBS_VALUE"]),
        "dato": felter["TIME_PERIOD"],
        "kilde": "ECB referencekurs EUR/DKK (data-api.ecb.europa.eu)",
        "hentet": "live",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="EUR/DKK-kurs fra ECB")
    ap.add_argument("--dkk", type=float, help="omregn dette beløb i kr. til euro")
    a = ap.parse_args()
    try:
        k = hent_ecb()
    except Exception as fejl:  # netværk, blokeret domæne, ændret format
        k = json.loads(RESERVE.read_text(encoding="utf-8"))
        k["hentet"] = f"reserve (ECB kunne ikke nås: {type(fejl).__name__})"
    if a.dkk is not None:
        k["dkk"] = a.dkk
        k["eur"] = round(a.dkk / k["kurs"], 2)
    print(json.dumps(k, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
