#!/usr/bin/env python3
"""Tjekker at pris-scriptet regner efter reglerne. Kør: python3 scripts/test_pris.py"""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "pris.py"


def pris(*args):
    r = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    return r.returncode, json.loads(r.stdout)


def main() -> int:
    tjek = []

    kode, p = pris("--postnr", "6430", "--land", "DK", "--paller", "2", "--vaegt", "900",
                   "--dato", "2026-10-06", "--kunde", "K1")
    tjek.append(("DK Syd, 2 paller, hverdag = 900 kr", kode == 0 and p["total_dkk"] == 900))

    kode, p = pris("--postnr", "6360", "--land", "DK", "--paller", "3", "--vaegt", "1500",
                   "--dato", "2026-10-10", "--kunde", "K4")
    tjek.append(("særaftale 400 x 3 + 25 % lørdag = 1.500 kr",
                  kode == 0 and p["prisgrundlag"] == "særaftale" and p["total_dkk"] == 1500))

    kode, p = pris("--postnr", "20457", "--land", "DE", "--paller", "5", "--vaegt", "4000",
                   "--dato", "2026-10-14", "--kunde", "K3")
    tjek.append(("DE Nord, 800 kg pr. palle = 10 pladser = 5.000 kr",
                  kode == 0 and p["pladser"] == 10 and p["total_dkk"] == 5000))

    kode, p = pris("--postnr", "8000", "--land", "DK", "--paller", "4", "--vaegt", "2400",
                   "--dato", "2026-10-08")
    tjek.append(("DK Øvrig, 4 paller = 2.600 kr, gyldig til 15/10",
                  kode == 0 and p["total_dkk"] == 2600 and p["gyldig_til"] == "2026-10-15"))

    kode, p = pris("--postnr", "6700", "--land", "DK", "--paller", "6", "--vaegt", "3000",
                   "--dato", "2026-10-09", "--kunde", "K2")
    tjek.append(("kreditspærret kunde får ingen pris", kode == 2 and p.get("stop") == "kreditspærret"))

    kode, p = pris("--postnr", "6000", "--land", "DK", "--paller", "1", "--vaegt", "500",
                   "--dato", "2026-04-03")
    tjek.append(("langfredag giver 25 % tillæg", kode == 0 and p["tillæg_grund"] == "langfredag"))

    for navn, ok in tjek:
        print(("OK   " if ok else "FEJL ") + navn)
    fejl = sum(1 for _, ok in tjek if not ok)
    print(f"{len(tjek) - fejl} af {len(tjek)} tjek bestået")
    return 1 if fejl else 0


if __name__ == "__main__":
    sys.exit(main())
