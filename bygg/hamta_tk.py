#!/usr/bin/env python3
"""
Hämtar lager från Trafikkontorets öppna data (OGC API Features) till GeoJSON.

  python3 bygg/hamta_tk.py --lista
  python3 bygg/hamta_tk.py Trafikflode_Cykel Cykelraknare
  python3 bygg/hamta_tk.py Cykelstrak_Linje --ut ../data

API:t ger max 100 objekt per anrop, så allt sidhanteras via "next"-länken.
Svaren kommer i WGS84 (EPSG:4326) trots att lagringen är SWEREF99 18 00
(EPSG:3011), alltså direkt användbara i Leaflet utan omprojicering.

Nyckeln läses ur .env i repotroten och ligger i URL-sökvägen. Den får aldrig
committas: .gitignore spärrar .env.
"""
import argparse, json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
BAS = "https://openstreetgs.stockholm.se/geoservice/api/{nyckel}/ogc/features/v1"


def las_nyckel() -> str:
    env = ROT / ".env"
    if not env.exists():
        sys.exit(f"Saknar {env}. Lägg TK_API_KEY där.")
    for rad in env.read_text(encoding="utf-8").splitlines():
        rad = rad.strip()
        if rad.startswith("TK_API_KEY="):
            return rad.split("=", 1)[1].strip()
    sys.exit("TK_API_KEY saknas i .env")


def hamta(url: str, forsok: int = 3) -> dict:
    for n in range(forsok):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as e:
            if n == forsok - 1:
                raise
            time.sleep(2 * (n + 1))
            print(f"    omförsök {n+1} efter {e}", file=sys.stderr)
    raise RuntimeError("oåtkomlig")


def maskera(text: str, nyckel: str) -> str:
    return text.replace(nyckel, "<NYCKEL>")


def lista_lager(bas: str, nyckel: str) -> None:
    d = hamta(f"{bas}/collections?f=application/json")
    cs = d.get("collections", [])
    print(f"{len(cs)} lager\n")
    for c in sorted(cs, key=lambda x: x.get("id", "")):
        print(f"  {c.get('id',''):<52} {(c.get('title') or '')[:56]}")


def hamta_lager(bas: str, nyckel: str, lager: str, utmapp: Path, limit: int = 100) -> Path | None:
    url = f"{bas}/collections/{lager}/items?f=application/json&limit={limit}"
    features, sidor, matchade = [], 0, None
    while url:
        d = hamta(url)
        if matchade is None:
            matchade = d.get("numberMatched")
        features.extend(d.get("features") or [])
        sidor += 1
        nasta = next((l["href"] for l in d.get("links", []) if l.get("rel") == "next"), None)
        if nasta == url:
            break
        url = nasta
        print(f"\r    {lager}: {len(features)} objekt, {sidor} sidor", end="", file=sys.stderr)
    print(file=sys.stderr)

    if not features:
        print(f"  !! {lager}: 0 objekt, hoppar över (skriver ingen fil)")
        return None
    if matchade is not None and len(features) != matchade:
        print(f"  !! {lager}: hämtade {len(features)} men API:t uppgav {matchade}")

    ut = utmapp / f"{lager}.geojson"
    ut.parent.mkdir(parents=True, exist_ok=True)
    ut.write_text(json.dumps(
        {"type": "FeatureCollection", "name": lager,
         "kalla": "Trafikkontoret öppna data, openstreetgs.stockholm.se",
         "hamtad": time.strftime("%Y-%m-%d"),
         "features": features},
        ensure_ascii=False), encoding="utf-8")
    mb = ut.stat().st_size / 1e6
    print(f"  OK {lager}: {len(features)} objekt, {mb:.1f} MB -> {ut.relative_to(ROT)}")
    return ut


def main() -> None:
    p = argparse.ArgumentParser(description="Hämta lager från Trafikkontorets öppna data")
    p.add_argument("lager", nargs="*", help="lagernamn, t.ex. Trafikflode_Cykel")
    p.add_argument("--lista", action="store_true", help="lista alla tillgängliga lager")
    p.add_argument("--ut", default=str(ROT / "bygg" / "cache"), help="utmapp")
    a = p.parse_args()

    nyckel = las_nyckel()
    bas = BAS.format(nyckel=nyckel)

    if a.lista:
        lista_lager(bas, nyckel)
        return
    if not a.lager:
        p.error("ange minst ett lagernamn, eller --lista")

    utmapp = Path(a.ut).resolve()
    print(f"Hämtar {len(a.lager)} lager till {utmapp}")
    for lager in a.lager:
        try:
            hamta_lager(bas, nyckel, lager, utmapp)
        except Exception as e:
            print(f"  FEL {lager}: {maskera(str(e), nyckel)}")


if __name__ == "__main__":
    main()
