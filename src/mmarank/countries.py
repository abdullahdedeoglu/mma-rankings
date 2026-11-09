"""Fighter country codes for the site's flags.

Fight Canon's nationality (from Sherdog, free text) first; where Fight Canon's copy is empty, the
same Sherdog field read by hand for listed fighters (data/external/sherdog_nationality_manual.csv);
then Wikidata via the Sherdog id (data/external/wikidata_sherdog_country.csv, CC0; see
scripts/wikidata_countries.py). Codes are lowercase ISO 3166-1 alpha-2, plus gb-eng, gb-sct,
gb-wls and gb-nir for the home nations, as Sherdog lists them.
"""

from __future__ import annotations

import csv
import re
import sqlite3
from pathlib import Path

from .config import EXTERNAL_DIR

_ALIASES = {
    "united states": "us", "usa": "us", "united stated": "us", "united staes": "us", "unidet states": "us",
    "vermont": "us", "new mexico": "us", "new hampshire": "us", "kansas": "us", "alaska": "us",
    "brazil": "br", "brasil": "br", "brazl": "br", "braz": "br", "bazil": "br", "sao paulo": "br", "belem": "br",
    "russia": "ru", "rus": "ru", "dagestan": "ru", "chechnya": "ru", "chechen": "ru",
    "japan": "jp", "poland": "pl", "england": "gb-eng", "scotland": "gb-sct", "wales": "gb-wls",
    "northern ireland": "gb-nir", "united kingdom": "gb", "isle of man": "im",
    "kyrgyzstan": "kg", "kyrgysztan": "kg", "kyryzstan": "kg", "kyr": "kg",
    "mexico": "mx", "méxico": "mx", "canada": "ca", "ontario": "ca", "ukraine": "ua", "ukr": "ua",
    "germany": "de", "alemania": "de", "uzbekistan": "uz", "france": "fr",
    "kazakhstan": "kz", "kazakstan": "kz", "argentina": "ar", "argentin": "ar",
    "australia": "au", "austraila": "au", "china": "cn", "south korea": "kr", "korea": "kr",
    "egypt": "eg", "italy": "it", "tajikistan": "tj", "tajikstan": "tj", "tadjikstan": "tj",
    "india": "in", "iran": "ir", "philippines": "ph", "phillipines": "ph", "afghanistan": "af", "afganistan": "af",
    "spain": "es", "peru": "pe", "azerbaijan": "az", "аzerbaijan": "az", "indonesia": "id", "indoensia": "id",
    "ecuador": "ec", "czech republic": "cz", "south africa": "za", "colombia": "co", "columbia": "co",
    "belarus": "by", "serbia": "rs", "georgia": "ge", "venezuela": "ve", "lithuania": "lt", "lituania": "lt",
    "netherlands": "nl", "the netherlands": "nl", "holland": "nl", "neatherlands": "nl", "netherlsna": "nl",
    "sweden": "se", "slovakia": "sk", "new zealand": "nz", "bulgaria": "bg", "finland": "fi", "croatia": "hr",
    "ireland": "ie", "turkey": "tr", "tukey": "tr", "romania": "ro", "greece": "gr", "austria": "at",
    "armenia": "am", "aremania": "am", "bolivia": "bo", "chile": "cl", "hungary": "hu", "portugal": "pt",
    "belgium": "be", "malaysia": "my", "moldova": "md", "latvia": "lv", "lativa": "lv", "vietnam": "vn",
    "uruguay": "uy", "switzerland": "ch", "paraguay": "py", "israel": "il", "mongolia": "mn",
    "costa rica": "cr", "iraq": "iq", "nigeria": "ng", "algeria": "dz", "dominican republic": "do",
    "denmark": "dk", "pakistan": "pk", "bosnia and herzegovina": "ba", "bosnia and hercegovina": "ba",
    "bosnia": "ba", "thailand": "th", "morocco": "ma", "norway": "no",
    "northern mariana islands": "mp", "northern marianas islands": "mp", "cameroon": "cm",
    "nicaragua": "ni", "slovenia": "si", "tunisia": "tn", "guam": "gu", "lebanon": "lb", "puerto rico": "pr",
    "guatemala": "gt", "aruba": "aw", "montenegro": "me", "congo, the democratic republic of the": "cd",
    "congo": "cg", "jordan": "jo", "turkmenistan": "tm", "taiwan": "tw", "panama": "pa", "cuba": "cu",
    "cambodia": "kh", "myanmar": "mm", "albania": "al", "honduras": "hn", "senegal": "sn",
    "el salvador": "sv", "bahrain": "bh", "angola": "ao", "cote d'ivoire": "ci", "ivory coast": "ci",
    "singapore": "sg", "united arab emirates": "ae", "estonia": "ee", "bangladesh": "bd",
    "macedonia": "mk", "fyrom": "mk", "kuwait": "kw", "cyprus": "cy", "benin": "bj", "syria": "sy",
    "uganda": "ug", "hong kong": "hk", "macao": "mo", "curacao": "cw", "zimbabwe": "zw", "saudi arabia": "sa",
    "trinidad and tobago": "tt", "libya": "ly", "ghana": "gh", "iceland": "is", "jamaica": "jm",
    "cape verde": "cv", "togo": "tg", "reunion": "re", "malta": "mt", "french polynesia": "pf",
    "zambia": "zm", "suriname": "sr", "nepal": "np", "sri lanka": "lk", "palestinian territory": "ps",
    "palestine": "ps", "liechtenstein": "li", "kenya": "ke", "sudan": "sd", "guinea": "gn",
    "burkina faso": "bf", "qatar": "qa", "south sudan": "ss", "oman": "om", "martinique": "mq", "haiti": "ht",
    "tanzania, united republic of": "tz", "samoa": "ws", "luxembourg": "lu", "kosovo": "xk", "belize": "bz",
    "tonga": "to", "sierra leone": "sl", "mali": "ml", "liberia": "lr", "guinea-bissau": "gw", "gambia": "gm",
    "gabon": "ga", "comoros": "km", "barbados": "bb", "yemen": "ye", "saint kitts and nevis": "kn",
    "papua new guinea": "pg", "namibia": "na", "mozambique": "mz", "monaco": "mc", "gibraltar": "gi",
    "french guiana": "gf", "guiana francesa": "gf", "equatorial guinea": "gq", "burundi": "bi",
    "brunei": "bn", "brunei darussalam": "bn", "virgin islands, u.s.": "vi", "somalia": "so",
    "sint maarten": "sx", "rwanda": "rw", "mauritius": "mu", "madagascar": "mg", "guadeloupe": "gp",
    "ethiopia": "et", "eritrea": "er", "chad": "td", "cayman islands": "ky", "bahamas": "bs",
    "andorra": "ad", "american samoa": "as", "bonaire, saint eustatius and saba": "bq",
}


def from_text(s: str | None) -> str | None:
    return _ALIASES.get(s.strip().lower()) if s else None


def _by_sherdog(path: Path, key: str, conv) -> dict[str, str]:
    if not path.exists():
        return {}
    with open(path, newline="") as fh:
        return {r["sherdog"]: c for r in csv.DictReader(fh) if (c := conv(r[key]))}


def load(db: sqlite3.Connection, csv_path: Path = EXTERNAL_DIR / "wikidata_sherdog_country.csv",
         manual_path: Path = EXTERNAL_DIR / "sherdog_nationality_manual.csv") -> dict[int, str]:
    out = {f: c for f, s in db.execute("SELECT fighter_id, nationality FROM fighters") if (c := from_text(s))}
    manual = _by_sherdog(manual_path, "nationality", from_text)
    wd = _by_sherdog(csv_path, "country", str.lower)
    for f, sid in db.execute("SELECT fighter_id, source_id FROM fighter_aliases WHERE source='sherdog'"):
        m = re.search(r"(\d+)$", sid)
        if f in out or not m:
            continue
        code = manual.get(m.group(1)) or wd.get(m.group(1))
        if code:
            out[f] = code
    return out
