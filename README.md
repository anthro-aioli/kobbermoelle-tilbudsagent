# Tilbudsagent · Kobbermølle Fragt ApS

Et lille repo der viser, hvordan en kodeagent (Codex i ChatGPT) kan behandle kundehenvendelser efter faste, skrevne regler: læse en indbakke, slå kunder op, regne prisen med et script, skrive svarudkast i mapper efter udfald og aflevere det hele som en pull request, som et menneske godkender. Intet sendes.

Kobbermølle Fragt ApS er en opdigtet vognmand i Padborg. Alle kunder, priser og henvendelser er opdigtede. Skift dem ud med dine egne, så har du en skabelon til din egen virksomhed.

## Hvad ligger hvor

- `AGENTS.md`: reglerne og arbejdsgangen. Det er den fil agenten læser først.
- `indbakke/`: én tekstfil pr. henvendelse.
- `data/kunder.json`: kunderegister med kreditspærring og særaftaler.
- `data/kurs.json`: reservekurs EUR/DKK, hvis det levende opslag fejler.
- `scripts/pris.py`, `scripts/kurs.py`, `scripts/test_pris.py`: prisberegning, valutakurs og selvtest.
- `udkast/`: her lander svarudkastene, fordelt på `tilbud/`, `afslag/`, `mangler-info/` og `eskalering/`.
- `status.csv`: én række pr. behandlet henvendelse.

## Sådan kører du det i Codex

1. Læg repoet på din egen GitHub-konto (fork eller kopi).
2. Åbn Codex i ChatGPT, forbind din GitHub-konto og vælg repoet.
3. Opret et miljø til repoet. Python 3 skal være tilgængeligt. Vil du have dagens valutakurs, så giv miljøet internetadgang til domænet `data-api.ecb.europa.eu`; ellers bruger scriptet reservekursen og siger det.
4. Giv Codex opgaven:

   > Behandl alle henvendelser i `indbakke/` efter `AGENTS.md`. Skriv ét udkast pr. henvendelse i den rigtige mappe under `udkast/`, opdatér `status.csv`, og kør `scripts/test_pris.py` til sidst. Åbn en pull request med det hele. Send ikke noget.

5. Læs pull requesten, som du ville læse en ny medarbejders udkast: rigtig mappe, rigtige tal, rigtig tone. Godkend, ret eller afvis. Først når du har godkendt, sender et menneske svarene.

## Gør det til dit eget

- Reglerne: skriv dine egne i `AGENTS.md`. Hold dem korte og nummererede, og skriv rækkefølgen, de skal tjekkes i.
- Kunderne: erstat indholdet i `data/kunder.json` med dine egne (samme felter).
- Zoner og priser: ret tabellen i `scripts/pris.py`.
- Indbakken: læg dine egne henvendelser i `indbakke/` (samme format som de otte, der ligger der).
- Kør `python3 scripts/test_pris.py` efter hver ændring i prisreglerne.

## Uden Codex

Har du ikke Codex, kan du indsætte `AGENTS.md` og én henvendelse i en almindelig chat og bede om et svarudkast. Så får du en reduceret øvelse: ingen scripts, intet kundeopslag, ingen pull request at godkende, og du skal selv kontrollere tallene.

Lavet til Business Aabenraa den 1. oktober 2026 af ai-savvy (ai-savvy.dk).
