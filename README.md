# Merroway Passport — The Passport Page of a Country That Isn't There

[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/c/the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/koiTalk/passport-page-merroway/rank.svg)](https://make.fun/c/the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/koiTalk/passport-page-merroway/reward.svg)](https://make.fun/c/the-passport-page-of-a-countr-2-20261121-0318)

An open passport spread for the invented tidal-island nation of Merroway,
drawn entirely in code: the data page of lighthouse keeper Elara Maren Voss
— bilingual Merroweg/English fields, a procedurally drawn portrait, a ghost
image, a script signature and a fully ICAO 9303-verified machine-readable
zone — facing a visas page with a Kergallen visitor visa, a tide notice for
the flooding causeway, and six entry/exit stamps, all dated after the
passport's issue. Merroway has no airfield, so the visa is valid for travel
by sea only.

## Run

```sh
python3 main.py
```

Writes `entry.png` (1024x1024) to `$MAKEFUN_OUTPUT_DIR` if set, otherwise
to `/output`. Pure Python 3 standard library, no network, no randomness —
two runs produce byte-identical output.
