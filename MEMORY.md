# Memory, kartrepot

_Last updated: 2026-09-02._

Persistent minne för kartarbetet. Ändras bara på Lars begäran. Ligger i git,
vilket betyder att det följer med till varje dator som klonar repot. Det är
avsiktligt: projektminnet i Claude gör inte det, mappminnet gör.

---

## Detta repo är kartans hem

**`larsstromgren.github.io` är den enda giltiga källan för publicerade
kartlager.** Beslutat 2026-09-02 efter en genomgång av hela datorn.

Kartarbete låg spritt på nio platser: detta repo, `~/kartor-statistik`,
`~/Geopandas`, `~/ai/kartprojekt`, `~/data`, `~/koder`, samt fyra mappar i
Dropbox. Tjugofyra HTML-kartor totalt, varav två publicerade och resten döda.

Det gav namnkrockar med olika innehåll:

- `tunnelbana.geojson` fanns i två versioner. Den i Cowork OS hade **noll**
  objekt, en misslyckad nedladdning på 246 byte. Repots version har 571.
- `valkretsar_mp.geojson` fanns i två versioner. Den i `~/data` saknade
  tidsserien `MP_pct_2014/2018/2022` som driver tidslinjesliden.

**Regeln som följer:** lager hämtas eller genereras hit, de kopieras inte hit.
`Cowork OS/AI och data/Geodata/` är inte längre datakälla.

Rollfördelning för de andra mapparna: `~/kartor-statistik` är analysbänken
(Movement Analytics, zondata). `~/Geopandas` är kursmaterial. `~/ai/kartprojekt`
är avslutat, men geofabrik-extractet och Nolli-tekniken där är värda att
återanvända.

---

## Trafikkontorets öppna data

**166 lager, gratis, bakom en API-nyckel.** Verifierat skarpt 2026-09-02.

- Nyckeln ligger i `.env` i repotroten, gitignorerad. Koordinatsystem
  SWEREF99 18 00, SRID 3011.
- **Nyckeln ligger i URL-sökvägen**, inte som parameter. Den kan alltså läcka
  via loggar och felmeddelanden, inte bara via git. `hamta_tk.py` maskerar den
  i sina felutskrifter.
- Hämtas med `python3 bygg/hamta_tk.py --lista` respektive
  `python3 bygg/hamta_tk.py <lager>`.

Fyra fynd som inte står i dokumentationen:

1. **Webbkatalogen visar 68 lager, API:t svarar med 166.** Det som saknas på
   webben är bland annat hela skyfallskarteringen, vinterväghållning per klass,
   sopsaltningsstråk, prioriterat gångnät, boendeparkering per område och
   parkeringstaxeområden. Lita på `/collections`, inte på webbsidan.
2. **Data levereras i WGS84 (EPSG:4326) trots att lagringen är EPSG:3011.**
   Svaren går rakt in i Leaflet utan omprojicering. Koordinaterna har tre
   värden, det tredje är höjd.
3. **Max 100 objekt per anrop.** Följer man inte `links[rel=next]` får man
   exakt 100 objekt, tyst, utan felmeddelande. `Cykelstrak_Linje` har 24 596.
4. **Hela `Trafikflode_Cykel` är märkt `Version 2017`.** Alla 1 020 sträckor.
   Får inte presenteras som nuläge. Toppvärden: Strömbron och Vasabron,
   12 000 cyklister per vardag.

Fullständig källkatalog, inklusive hackathonets femtio externa källor, finns i
`Cowork OS/statistik/KALLOR-geodata.md`.

---

## Vad som inte får publiceras

Repot är **publikt**. GitHub Pages har ingen inloggning på gratisnivå. Allt som
läggs i `data/` blir nedladdningsbart av vem som helst.

Detta hör inte hemma här:

- **Movement Analytics.** Kommer från The Train Brains publika säljdemo, är
  inte licensierad data, och 10-kommunjämförelsen är underlag till en rapport
  från Dagens industri med embargoliknande status. Se
  `~/kartor-statistik/Movement Analytics/MEMORY.md`.
- **Egna skattningar som kan förväxlas med källans.** Måttet "bilfrihet för
  korta resor" är Lars approximation, inte Train Brains definition.
- **MP-data.** `valkretsar_mp.geojson` är partiets resultat per valdistrikt
  över tre val. Valresultat är offentliga, men en karta över var partiet är
  starkt, publicerad under Lars namn som sittande trafikborgarråd, är
  partiarbete och inte stadens.

**Läget 2026-09-02:** `data/movementanalytics_zoner.geojson` ligger uppe och är
publikt nedladdningsbar. Den laddades upp via GitHubs webbgränssnitt
2026-08-12. Alla 127 zoner med `car_pct`, `sustainable_pct`, åldersfördelning,
könsfördelning och maxtimme. Beslut om den ska ligga kvar är inte fattat.

**Planerad lösning:** dela upp i två sidor med samma kodbas. En publik med
enbart öppna data, och en privat på Cloudflare Pages bakom Cloudflare Access,
gratis upp till 50 användare. Ett byggskript med en flagga avgör vilka lager
som följer med, så att ett känsligt lager inte kan råka publiceras genom ett
slarvigt `git add`.

Hackathonutmaningen "Framtidens hållbara och hälsosamma städer", där Lars satt
i juryn, är avklarad per 2026-09-02 och styr inget framåt.
