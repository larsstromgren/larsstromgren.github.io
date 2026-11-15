#!/usr/bin/env python3
"""Bygger byggnadslagret ur ArkDes dataset "Byggnader i Sverige" på KulturNav.

    python3 bygg/bygg_byggnader.py           hela bygget
    python3 bygg/bygg_byggnader.py --test    provanrop, visar svarens struktur

Körs från repots rot eller var som helst: sökvägarna utgår från skriptets plats.
Bara standardbiblioteket, ingen pip install.

Varför skriptet körs på datorn och inte av Claude: kulturnav.org nås inte från
Claudes miljöer (testat 2026-06-11 och 2026-11-15). Din Mac når det utan problem.

Så går det till:

Skriptet använder KulturNavs Core API (https://kulturnav.org/info/api-core):

    /api/core/entityType:Building,entity.dataset:<uuid>/<offset>/<antal>
        ?properties=caption,entity.latitude,entity.longitude,superconcept.begin

Namn, koordinater och byggår kommer då med direkt i listningen, hundra
byggnader per anrop, cirka 45 anrop för hela datasetet. Byggnader utan
koordinater och byggnader utanför Stockholms kommun (bounding box) sorteras bort.

Byggnader utan koordinater i listningen har ingen punkt alls: deras egen
GeoJSON (kulturnav.org/<uuid>.geojson) är en tom sida, inte JSON. Verifierat
2026-11-15 på Cloettas kiosk, Stockholmsutställningen 1930. Någon reservväg
behövs alltså inte.

Datasetet hade 4 441 byggnader 2026-11-15. Datumen har formen "1898-Y".

Lärdom 2026-11-15: det äldre sök-API:t (/api/search/...,dataset:<uuid>) svarar
med en tom lista för det här datasetet. Filtret heter entity.dataset i Core API.

Licens: CC0. Förvaltas av ArkDes via KulturNav.

Indata:
    https://kulturnav.org, dataset 1f23ddae-5579-4e3e-bf59-a29524e4f926

Utdata:
    data/byggnader_arkdes.geojson   (punkter, EPSG:4326)
"""

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DATASET = "1f23ddae-5579-4e3e-bf59-a29524e4f926"   # Byggnader i Sverige (ArkDes)
BASE = "https://kulturnav.org"
CORE = f"{BASE}/api/core/entityType:Building,entity.dataset:{DATASET}"
PROPS = "caption,entity.latitude,entity.longitude,superconcept.begin"
PAGE = 100
PAUS = 0.3   # sekunder mellan anrop, av hänsyn till KulturNav

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "data" / "byggnader_arkdes.geojson"

# Stockholms kommun. Vidga till länet vid behov: lon 17.6-18.6, lat 58.9-59.7
BBOX = {"lon_min": 17.75, "lon_max": 18.20, "lat_min": 59.23, "lat_max": 59.43}

HEADERS = {"User-Agent": "larsstromgren.github.io byggnadslager"}


def get_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def page_url(offset, n):
    return f"{CORE}/{offset}/{n}?properties={PROPS}&displayValues=true&lang=sv"


def plain(v):
    """Gör om ett egenskapsvärde till text eller tal, oavsett inslagning."""
    if isinstance(v, list):
        return plain(v[0]) if v else None
    if isinstance(v, dict):
        for key in ("displayValue", "value"):
            if key in v:
                return plain(v[key])
        for lang in ("sv", "en", "no", "*"):
            if lang in v:
                return plain(v[lang])
        return None
    return v


def prop(entity, name):
    """Hämta en egenskap ur en post, vare sig properties är ett objekt eller en lista."""
    props = entity.get("properties")
    if isinstance(props, dict):
        return plain(props.get(name))
    if isinstance(props, list):
        for p in props:
            if isinstance(p, dict) and name in (p.get("propertyType"), p.get("type"), p.get("name")):
                return plain(p)
    return None


def number(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


def year_of(v):
    m = re.search(r"\d{4}", str(v or ""))
    return int(m.group()) if m else None


def in_stockholm(lon, lat):
    return (BBOX["lon_min"] <= lon <= BBOX["lon_max"]
            and BBOX["lat_min"] <= lat <= BBOX["lat_max"])


def to_feature(e):
    uuid = e.get("uuid")
    name = plain(e.get("caption")) or prop(e, "caption") or plain(e.get("name"))
    year = year_of(prop(e, "superconcept.begin"))
    lat, lon = number(prop(e, "entity.latitude")), number(prop(e, "entity.longitude"))
    if lat is None or lon is None:
        return None, "utan_punkt"
    if not in_stockholm(lon, lat):
        return None, "utanfor"
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
        "properties": {
            "name": name or "Byggnad",
            "year": year,
            "uuid": uuid,
            "url": f"{BASE}/{uuid}",
        },
    }, "ok"


def test():
    url = page_url(0, 3)
    print(f"Anrop: {url}\n")
    data = get_json(url)
    print(json.dumps(data, ensure_ascii=False, indent=2)[:4000])
    for e in (data.get("entities") or [])[:3]:
        print("\nBlir i lagret:", to_feature(e))
    print(f"\nAntal byggnader i datasetet: {data.get('totalHits')}")


def main():
    if "--test" in sys.argv:
        test()
        return

    features, utfall, offset, total = [], {}, 0, None
    while True:
        try:
            data = get_json(page_url(offset, PAGE))
        except (urllib.error.URLError, TimeoutError) as err:
            sys.exit(f"Anropet på offset {offset} misslyckades: {err}. Kör skriptet igen.")
        total = data.get("totalHits", total)
        entities = data.get("entities") or []
        if not entities:
            if offset == 0:
                sys.exit("Inga byggnader i svaret. Kör med --test och visa utskriften för Claude.")
            break
        for e in entities:
            feat, status = to_feature(e)
            utfall[status] = utfall.get(status, 0) + 1
            if feat:
                features.append(feat)
        offset += len(entities)
        print(f"  {offset}/{total or '?'} genomgångna, {len(features)} i Stockholm", file=sys.stderr)
        if len(entities) < PAGE or (total and offset >= total):
            break
        time.sleep(PAUS)

    features.sort(key=lambda x: (x["properties"]["year"] or 9999, x["properties"]["name"]))
    OUT.write_text(json.dumps({"type": "FeatureCollection", "features": features},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    utan_ar = sum(1 for x in features if x["properties"]["year"] is None)
    print(f"\nKlart: {len(features)} byggnader i Stockholm, varav {utan_ar} utan byggår.")
    print(f"Utfall: {utfall}")
    print(f"Skrivet till {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
