"""Refresh data/external/wikidata_sherdog_country.csv (CC0): Sherdog id -> country (ISO 3166-1 alpha-2).

Country for sport (P1532) when Wikidata has it, otherwise citizenship (P27) when there is
exactly one. Fighters with several citizenships and no P1532 are left out (no guess).
Used only where Fight Canon has no nationality. Run: python3 scripts/wikidata_countries.py
"""

import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "external" / "wikidata_sherdog_country.csv"
UA = "mma-rankings-research/0.1 (https://github.com/abdullahdedeoglu/mma-rankings)"
QUERY = """
SELECT ?sherdog (GROUP_CONCAT(DISTINCT ?sport; separator="|") AS ?sports)
                (GROUP_CONCAT(DISTINCT ?cit; separator="|") AS ?cits) WHERE {
  ?p wdt:P2818 ?sherdog .
  OPTIONAL { ?p wdt:P1532 ?s . ?s wdt:P297 ?sport . }
  OPTIONAL { ?p wdt:P27 ?c . ?c wdt:P297 ?cit . }
} GROUP BY ?sherdog
"""


def main() -> None:
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": QUERY, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    rows = json.load(urllib.request.urlopen(req, timeout=300))["results"]["bindings"]
    out = []
    for r in rows:
        sid = r["sherdog"]["value"].strip()
        sports = [x for x in r.get("sports", {}).get("value", "").split("|") if x]
        cits = [x for x in r.get("cits", {}).get("value", "").split("|") if x]
        code = sports[0] if len(sports) == 1 else (cits[0] if len(cits) == 1 and not sports else None)
        if code and sid.isdigit():
            out.append((int(sid), code.upper()))
    out.sort()
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sherdog", "country"])
        w.writerows(out)
    print(f"{len(out)} fighters -> {OUT}")


if __name__ == "__main__":
    main()
