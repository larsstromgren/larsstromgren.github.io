#!/usr/bin/env python3
"""Bygger stadsdelsområdeslagret med befolkning, areal och täthet.

    python3 bygg/bygg_stadsdelsomraden.py

Varför just den här nivån, och inte stadsdel:

Stockholms statistik och stadskartan använder två olika begrepp som båda heter
"stadsdel". Stadskartan har 117 polygoner (Vasastaden, Södermalm, Årsta).
Statistiken har 135 områden som i innerstaden är församlingsbaserade (Klara,
Jakob, Gustav Vasa, Hedvig Eleonora, Östra Katarina).

Mätt 2026-10-02: kopplar man statistikens stadsdelar till stadskartans
polygoner på namn matchar bara 101 av 135, och **310 186 personer, 31,2 procent
av staden, faller bort**. Bortfallet är nästan uteslutande innerstaden.
16 polygoner blir helt utan siffror, bland dem Norrmalm, Vasastaden,
Södermalm, Östermalm, Kungsholmen och Gamla Stan.

Stadsdelsnivån går alltså inte att använda för stadens egen statistik.
Stadsdelsområde gör det, eftersom varje statistikrad har en känd förälder i
källfilens hierarki. Summan stämmer exakt mot filens egen rad "Hela staden",
995 574 personer.

Två fällor i källorna som skriptet hanterar:

1. Geometrin har **13** nämndområden, indelningen före 2023-07-01, trots att
   leveransen är nyare. Norrmalm + Östermalm slås ihop till Norra innerstaden,
   Rinkeby-Kista + Spånga-Tensta till Järva. Då blir det dagens 11.
2. Statistikfilen har en egen rad för **Älvsjö** med gammal nämndkod, utöver
   Hägersten - Älvsjö. Den måste uteslutas, annars dubbelräknas 33 605
   personer. Filen skriver dessutom namnen med blanksteg runt bindestreck
   ("Hässelby - Vällingby") där geometrin inte gör det.

Indata:
    Cowork OS/Trafiknämnden/Stadsdelsdatabas/geodata/shp/Adm_area.shp
    Cowork OS/statistik/2.4-areal-och-befolkningstathet-...-2024-12-31.xlsx

Utdata:
    data/stadsdelsomraden.geojson   (11 polygoner, EPSG:4326)
"""
import re
import sys
import unicodedata
from pathlib import Path

import geopandas as gpd
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
VALV = Path("/Users/larsstromgren/Dropbox (Personlig)/Cowork OS")
ADM = VALV / "Trafiknämnden/Stadsdelsdatabas/geodata/shp/Adm_area.shp"
STAT = VALV / ("statistik/2.4-areal-och-befolkningstathet-i-stadsdelsomraden-"
               "sdn-delar-och-stadsdelar-2024-12-31.xlsx")
UT = REPO / "data/stadsdelsomraden.geojson"

# Indelningen före 2023-07-01 i geometrin, mappad till dagens 11 områden.
SLÅ_IHOP = {
    "Norrmalm": "Norra innerstaden",
    "Östermalm": "Norra innerstaden",
    "Rinkeby-Kista": "Järva",
    "Spånga-Tensta": "Järva",
}

# Rader i statistikfilen som bär nämndkod från före 2023 och dubbelräknar.
UTESLUT = {"ÄLVSJÖ"}

REGIONER = {"Västerort", "Söderort", "Innerstaden", "Inre staden",
            "Yttre staden", "Hela staden", "Totalt"}


def nyckel(s: str) -> str:
    """Normaliserar ett områdesnamn så att källorna går att jämföra.

    Vaulten är NFD-normaliserad på macOS, så NFC först. Statistikfilen skriver
    "Hässelby - Vällingby", geometrin "Hässelby-Vällingby".
    """
    s = unicodedata.normalize("NFC", str(s))
    s = re.sub(r"\s*-\s*", "-", s)
    return re.sub(r"\s+", " ", s).strip().upper()


def las_statistik() -> pd.DataFrame:
    raw = pd.read_excel(STAT, header=None)
    rader = []
    for _, r in raw.iloc[4:].iterrows():
        kod, namn = r[0], r[1]
        if not isinstance(namn, str) or not namn.strip():
            continue
        namn = namn.strip()
        if namn in REGIONER or pd.isna(kod):
            continue
        if not re.fullmatch(r"\d+(\.0)?", str(kod).strip()):
            continue  # bara hela tal är områdesnivå, "1.1" är SDN-del
        try:
            folk = int(r[5])
            land, vatten = int(r[2]), (0 if str(r[3]).strip() == "–" else int(r[3]))
        except (TypeError, ValueError):
            continue
        if nyckel(namn) in UTESLUT:
            print(f"  utesluter dubbelräknad rad: {namn} ({folk} personer)")
            continue
        rader.append({"nyckel": nyckel(namn), "omrade": namn,
                      "folkmangd": folk, "areal_land_ha": land,
                      "areal_vatten_ha": vatten})
    return pd.DataFrame(rader)


def las_geometri() -> gpd.GeoDataFrame:
    g = gpd.read_file(ADM)
    g = g[g["GRUPP"] == "Stadsdelsnämndsområde"].copy()
    print(f"  geometrin har {len(g)} nämndområden (indelningen före 2023-07-01)")
    g["omrade_namn"] = g["NAMN"].replace(SLÅ_IHOP)
    g = g.dissolve(by="omrade_namn", as_index=False)
    print(f"  efter ihopslagning: {len(g)} områden")
    g["nyckel"] = g["omrade_namn"].map(nyckel)
    return g[["nyckel", "omrade_namn", "geometry"]]


def main() -> int:
    print("Läser statistik")
    stat = las_statistik()
    print(f"  {len(stat)} områden, summa {stat.folkmangd.sum():,} personer"
          .replace(",", " "))

    print("Läser geometri")
    geo = las_geometri()

    bara_geo = set(geo.nyckel) - set(stat.nyckel)
    bara_stat = set(stat.nyckel) - set(geo.nyckel)
    if bara_geo or bara_stat:
        print(f"  !! matchar inte: bara i geometri {sorted(bara_geo)}, "
              f"bara i statistik {sorted(bara_stat)}")
        return 1
    print("  alla områden matchar på namn, inget bortfall")

    df = geo.merge(stat, on="nyckel", how="inner")
    df["tathet_inv_per_ha_land"] = (df.folkmangd / df.areal_land_ha).round(2)
    df["areal_totalt_ha"] = df.areal_land_ha + df.areal_vatten_ha
    df["kalla"] = "Stockholms statistiska årsbok tabell 2.4, 2024-12-31"

    df = df.drop(columns=["nyckel"]).to_crs(4326)
    df.to_file(UT, driver="GeoJSON")

    print(f"\nSkrev {UT.relative_to(REPO)}")
    print(f"  {len(df)} polygoner, {UT.stat().st_size/1e6:.1f} MB, EPSG:4326")
    print(f"  befolkning totalt: {df.folkmangd.sum():,}".replace(",", " "))
    print("\n  tätast befolkade områden, invånare per hektar land:")
    for _, r in df.nlargest(4, "tathet_inv_per_ha_land").iterrows():
        print(f"    {r.tathet_inv_per_ha_land:>7.2f}  {r.omrade_namn}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
