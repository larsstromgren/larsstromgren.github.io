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

## Det olösta

**"Stadsdel" betyder två olika saker.** Stadskartans 117 stadsdelar mot
statistikens 132 Nyko 5-områden. I ytterstaden sammanfaller de i stort, i
innerstaden inte alls. Kopplas befolkningsstatistik till kartpolygoner på namn
uppstår tyst bortfall i innerstaden. Beslut om vilket begrepp som ska gälla,
eller om båda ska finnas som parallella dimensioner, är inte fattat. Hela
resonemanget står i `Stadsdelsdatabas/ANTECKNINGAR.md`.

**Scenariomotorn är inte byggd.** Planerad som tre typer, där ett scenario är
en JSON-fil och aldrig en kodändring:

- **Visa**, byt variabel på samma geometri
- **Räkna**, härled ett nytt mått ur flera lager
- **Jämför**, ställ två tillstånd mot varandra, exempelvis nuläge mot utbyggd
  cykelplan. Tidslinjesliden i `index.html` är färdigt gränssnitt för detta.
