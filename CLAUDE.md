# CLAUDE.md, kartrepot

Kartor över Stockholm för Lars Strömgren, trafikborgarråd. Leaflet, publicerat
via GitHub Pages på https://larsstromgren.github.io/

**Läs `MEMORY.md` i denna mapp innan du börjar.** Den innehåller besluten som
måste överleva mellan sessioner.

---

## Regler

1. **Svara på svenska.**
2. **Inga tankstreck** (— eller –) i text som publiceras i Lars namn. Skriv om
   med komma, punkt eller kolon. Gäller även engelska. Sök på "—" före leverans.
3. **Repot är publikt.** Kontrollera vad ett lager innehåller innan det läggs i
   `data/`. Se avsnittet om vad som inte får publiceras i `MEMORY.md`.
4. **API-nyckeln ligger i `.env` och får aldrig committas.** Kör
   `git diff --cached --name-only` före varje commit och kontrollera att
   `.env` inte är med.
5. **En karta, inte många.** Skriv över, versionera i git. Skapa aldrig
   `karta_2.html`. Det var precis så det gick fel förut: tjugofyra HTML-kartor
   på nio platser, ingen som visste vilken som gällde.
6. **Lager genereras, de kopieras inte.** Allt i `data/` ska gå att bygga om
   från en källa via `bygg/`.

---

## Struktur

```
├── index.html          Kartan. Leaflet, lagerkontroll, teckenförklaring, tidslinje
├── cykelpotential.html Separat sida, makroområden
├── data/               Publicerade lager, GeoJSON. Genererade, ej handredigerade
├── bygg/               Skript som bygger data/
│   ├── hamta_tk.py     Hämtar från Trafikkontorets öppna data
│   └── cache/          Råhämtningar. Gitignorerad
├── .env                API-nyckel. Gitignorerad
├── CLAUDE.md           Denna fil
└── MEMORY.md           Persistent minne
```

---

## Var underlaget finns

| Vad | Var |
|---|---|
| Källkatalog, alla datakällor | `Cowork OS/statistik/KALLOR-geodata.md` |
| Stadens statistik, xlsx | `Cowork OS/statistik/` |
| Analysbänk, Movement Analytics | `~/kartor-statistik/` |
| Stadsdelsgeografi och Nyko-problemet | `Cowork OS/Trafiknämnden/Stadsdelsdatabas/` |
| OSM Sverige-extract, land_polygons | `~/ai/kartprojekt/geofabrik/` |

---

## Avgjort 2026-10-02: stadsdelsområde för statistik, stadsdel för geografi

**"Stadsdel" betyder två olika saker,** och frågan om vilket begrepp som gäller
är nu avgjord genom mätning, inte val.

Kopplas stadens statistik till stadskartans 117 polygoner på namn matchar bara
**101 av 135** rader, och **310 186 personer, 31,2 procent av staden, faller
bort**. Bortfallet är nästan uteslutande innerstaden, där statistiken räknar
församlingar (Klara, Jakob, Gustav Vasa, Hedvig Eleonora, Östra Katarina) och
kartan räknar stadsdelar. Sexton polygoner blir helt utan siffror, bland dem
Norrmalm, Vasastaden, Södermalm, Östermalm, Kungsholmen och Gamla Stan.

**Regeln:**

- **Stadens egen statistik läggs på stadsdelsområde**, elva stycken, där
  bortfallet är noll. Lagret byggs av `bygg/bygg_stadsdelsomraden.py` och
  ligger i `data/stadsdelsomraden.geojson`.
- **De 117 stadsdelarna används för geografi** och för mått vi räknar ut själva,
  där stadens befolkningstabell inte behövs, till exempel avstånd till ett
  cykelstråk.

Det fungerar eftersom varje statistikrad har en känd förälder i källfilens egen
hierarki: Klara under Södra Norrmalm under Norra innerstaden. Verifierat mot
filens rad "Hela staden": 991 937 i lagret plus 3 637 på kommunen skrivna blir
995 574.

Bakgrunden står i `Stadsdelsdatabas/ANTECKNINGAR.md`, men notera att den filens
uppgift om att en nyckeltabell måste beställas från Sweco är överspelad.

## Det olösta

**Scenariomotorn är inte byggd.** Planerad som tre typer, där ett scenario är
en JSON-fil och aldrig en kodändring:

- **Visa**, byt variabel på samma geometri
- **Räkna**, härled ett nytt mått ur flera lager
- **Jämför**, ställ två tillstånd mot varandra, exempelvis nuläge mot utbyggd
  cykelplan. Tidslinjesliden i `index.html` är färdigt gränssnitt för detta.
