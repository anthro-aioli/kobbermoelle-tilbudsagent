#!/usr/bin/env python3
"""Seks end-to-end-tjek af prisberegneren."""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "pris.py"


def koer(*argumenter):
    proces = subprocess.run(
        [sys.executable, str(SCRIPT), *argumenter],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return proces.returncode, json.loads(proces.stdout)


def main():
    tjek = []

    kode, svar = koer("--postnr", "6430", "--land", "DK", "--paller", "2", "--vaegt", "900", "--dato", "2026-10-06", "--kunde", "K1")
    tjek.append(kode == 0 and svar["total_dkk"] == 900)

    kode, svar = koer("--postnr", "6360", "--land", "DK", "--paller", "3", "--vaegt", "1500", "--dato", "2026-10-10", "--kunde", "K4")
    tjek.append(kode == 0 and svar["prisgrundlag"] == "særaftale" and svar["total_dkk"] == 1500)

    kode, svar = koer("--postnr", "20457", "--land", "DE", "--paller", "5", "--vaegt", "4000", "--dato", "2026-10-14", "--kunde", "K3")
    tjek.append(kode == 0 and svar["pladser"] == 10 and svar["total_dkk"] == 5000 and svar["total_eur"] == 668.86)

    kode, svar = koer("--postnr", "8000", "--land", "DK", "--paller", "4", "--vaegt", "2400", "--dato", "2026-10-08")
    tjek.append(kode == 0 and svar["total_dkk"] == 2600 and svar["gyldig_til"] == "2026-10-15")

    kode, svar = koer("--postnr", "6700", "--land", "DK", "--paller", "6", "--vaegt", "3000", "--dato", "2026-10-09", "--kunde", "K2")
    tjek.append(kode == 2 and svar == {"stop": "kreditspærret"})

    kode, svar = koer("--postnr", "6000", "--land", "DK", "--paller", "1", "--vaegt", "500", "--dato", "2026-04-03")
    tjek.append(kode == 0 and svar["tillæg_grund"] == "langfredag")

    for nummer, bestaaet in enumerate(tjek, start=1):
        print(f"Tjek {nummer}: {'OK' if bestaaet else 'FEJL'}")
    print(f"{sum(tjek)} af 6 tjek bestået")
    return 0 if all(tjek) else 1


if __name__ == "__main__":
    sys.exit(main())
