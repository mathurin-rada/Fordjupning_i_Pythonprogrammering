# Kodgranskning av originalet

Granskningen avser den oförändrade filen `original/order_report.py`. Radnumren nedan avser den filen, inte den nya startpunkten. ZIP-filen innehöll endast denna Pythonfil, `data/orders.csv` och en tom `output/`-katalog. Båda projektfilerna lästes före ändringarna. Startpunkten var modulens toppnivå.

## 1. Flera ansvar i ett enda körblock

**Observation:** Rader 9–217 läser data, validerar, normaliserar, beräknar och skriver rapporter utan funktioner.

**Konsekvens:** En enskild beräkning kan inte testas utan filinläsning och rapportskrivning.

**Förslag:** Dela upp ansvaret i `file_io`, `validation`, `processing` och `reporting` och låt en liten startpunkt anropa dem.

## 2. Sidoeffekter vid import

**Observation:** Utskrift på rad 7, inläsning på rad 10 och rapportskrivning från rad 93 körs direkt när modulen importeras. `main()` och startpunktsskydd saknas.

**Konsekvens:** Import kan läsa och skriva filer, vilket försvårar återanvändning och testning.

**Förslag:** Inför `main()` och `if __name__ == "__main__"`. Konfigurera logging först vid körning.

## 3. Duplicerad sammanställning

**Observation:** Rader 103–131 och 143–171 gör samma aggregering, avrundning och sortering för kategori respektive region. Rader 183–206 upprepar delar av returlogiken.

**Konsekvens:** En rättning måste göras på flera ställen och kan ge olika beteenden.

**Förslag:** Skapa en gemensam sammanställningsfunktion med gruppkolumn och ett val för försäljningskolumnen. Bevara kolumnordning och sortering.

## 4. Otydliga fel och för bred felhantering

**Observation:** Rad 25 kastar `Exception("Fel data")`. Rader 219–220 fångar alla vanliga undantag och skriver ett meddelande.

**Konsekvens:** Användaren får inte veta vilka kolumner som saknas. Även programmeringsfel fångas, och skriptet signalerar inte misslyckande med en uttrycklig felkod.

**Förslag:** Använd `DataValidationError` med konkreta meddelanden, fånga förväntade fil- och datafel vid startpunkten och returnera felkod 1.

## 5. Tysta ersättningar och saknad rimlighetskontroll

**Observation:** Rader 38–51 ersätter ogiltigt/saknat antal med 1, pris med median och rabatt med 0. Rader 53–60 gör alla okända returvärden falska. Kontroller av tom data, negativa priser och rabattintervall saknas.

**Konsekvens:** Dataproblem blir osynliga. Om alla priser saknas finns ingen användbar median. Orimliga värden kan påverka försäljningen.

**Förslag:** Behåll originalets ersättningsregler med varningar. Stoppa tydligt vid oanvändbar data och dokumentera nya gränskontroller. Ändra inte returernas betydelse.

## 6. Körinformation med print

**Observation:** Rader 7, 27, 101, 141, 181 och 216–220 använder `print()` för status och fel.

**Konsekvens:** Status, varningar och fel saknar loggnivåer och modulkontext.

**Förslag:** Konfigurera logging centralt och använd `logging.getLogger(__name__)` i moduler som läser, validerar och skapar/sparar rapporter.

## 7. Hårdkodade sökvägar och förutsatt utdatakatalog

**Observation:** Rader 4–5 anger relativa sökvägar. Skrivningen från rad 93 förutsätter att `output/` redan finns; ingen katalog skapas i koden.

**Konsekvens:** Körning är beroende av aktuell arbetskatalog och en förberedd utdatakatalog.

**Förslag:** Behåll standardsökvägarna men låt dem anges via argument och en liten `ReportConfig`-dataclass. Skapa utdatakatalogen vid sparande.

## 8. Namngivning och avsaknad av skyddande tester

**Observation:** `result1` och `result2` på rader 103 respektive 143 beskriver inte rapporternas innehåll. Arkivet innehåller inga tester, beroendefiler eller README. Importerna på rader 1–2 är redan explicita; wildcard-importer och sys.path-hack finns inte.

**Konsekvens:** Det är svårare att förstå resultaten och upptäcka oavsiktliga ändringar i försäljning, orderantal och returer.

**Förslag:** Ge funktioner beskrivande namn, behåll explicita importer och inför små pytest-fall samt jämförelse mot rapporter från en faktisk originalkörning.

## Verifierat originalbeteende

Originalet kördes från den uppackade projektroten med Python 3.12.14 och pandas 3.0.1. Körningen lyckades utan rapporterade programfel och läste 80 rader. Konsolen skrev start, antal rader, fyra sparade filnamn och `Klart`. Den första konsolvisningen hade felvisade svenska tecken; detta hindrade inte rapportskapandet.

| Rapport | Resultat |
| --- | --- |
| overview.csv | total_sales 138036.05; order_count 80; return_count 15 |
| sales_by_category.csv | Electronics 79589.30; Sports 24416.15; Home 23927.60; Books 10103.00 |
| sales_by_region.csv | South 36737.95; East 35585.35; West 32624.80; North 29891.95; Unknown 3196.00 |
| returns_by_category.csv | Electronics 7/26 = 0.269; Home 4/17 = 0.235; Sports 2/16 = 0.125; Books 2/21 = 0.095 |

De fyra fullständiga originalrapporterna finns i `tests/baseline/`. De kopierades från originalkörningen innan refaktoreringen kördes.

Originalets regler som måste bevaras:

- `order_value = quantity * unit_price`; `discounted_value = order_value * (1 - discount)`.
- Returer ingår i försäljningssumman. Order räknas som unika order-ID, returer som antalet sanna rader. Därför kan returandel överstiga 1 om samma order-ID förekommer på flera returrader.
- Försäljning avrundas efter summering till två decimaler; returandel till tre. Ingen radvis avrundning läggs till.
- Gruppnamn normaliseras med trimning och title case. Saknade gruppnamn blir `Unknown`.
- Försäljningsrapporter sorteras fallande på försäljning, returrapporten på returandel.
- Datum och kund-ID krävs som kolumner men används inte i beräkningarna.

I levererad CSV finns saknad rabatt på O0013, saknat antal på O0028, saknad region på O0032, rabatt `unknown` på O0040, saknat pris på O0062 och saknad returflagga på O0069. Dessa behandlas enligt originalet. Medianpriset är 499.0.
