# Orderrapportering

En liten refaktorering av det medföljande Pythonprogrammet. Programmet läser orderdata och skapar samma fyra CSV-rapporter som originalet. Det använder pandas för tabeller och pytest för tester.

## Installation och körning

Kräver Python 3.11 eller senare. Verifierad miljö: Python 3.12.14, pandas 3.0.1 och pytest 8.3.5 på Windows. Öppna en terminal i projektroten, alltså katalogen med denna README.

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe order_report.py
.\.venv\Scripts\python.exe -m pytest -v
```

Om `py` saknas, använd `python` eller sökvägen till din installerade Python. På macOS/Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python order_report.py
.venv/bin/python -m pytest -v
```

Alternativa sökvägar:

```powershell
.\.venv\Scripts\python.exe order_report.py --input data/orders.csv --output output
```

Relativa sökvägar utgår från terminalens arbetskatalog. Ange absoluta sökvägar vid körning från en annan katalog. Utdatakatalogen skapas automatiskt. Körningen skriver över de fyra rapportfilerna med samma namn. Loggar går till terminalen; lyckad körning ger exitkod 0 och förväntade fel ger 1. Ett skrivfel kan lämna delvis uppdaterade rapporter; sparandet är inte en transaktion.

## Projektstruktur och ansvar

```text
order_report_project/
├── order_report.py            # main, argument, central logging, körflöde
├── order_reporting/
│   ├── __init__.py
│   ├── config.py              # ReportConfig med in- och utdatasökväg
│   ├── file_io.py             # CSV-inläsning och sparande
│   ├── validation.py          # kontroller och originalets normalisering
│   ├── processing.py          # ordervärden och gruppsammanställning
│   └── reporting.py           # bygger de fyra rapporttabellerna
├── data/orders.csv            # oförändrad originaldata
├── output/                    # fyra genererade CSV-rapporter
├── original/order_report.py   # oförändrad kod för granskning
├── tests/
│   ├── baseline/              # fyra rapporter från originalkörningen
│   ├── conftest.py            # tre kontrollerade orderrader
│   ├── test_processing.py
│   ├── test_validation.py
│   └── test_integration.py
├── requirements.txt
├── .gitignore
├── code_review.md
├── reflection.md
├── verification.md
└── checklist.md
```

`ReportConfig` samlar de två sökvägarna i ett tydligt, oföränderligt konfigurationsobjekt. Tester kan använda tillfälliga kataloger utan att ändra globala variabler. Klassen gör ingen filhantering och innehåller inte programmets logik.

## Rapporter och beräkningsregler

| Fil i output/ | Innehåll |
| --- | --- |
| overview.csv | Försäljning efter rabatt, unika order och antal returrader |
| sales_by_category.csv | Orderantal, försäljning, returer och returandel per kategori |
| sales_by_region.csv | Samma mått per region |
| returns_by_category.csv | Orderantal, returer och returandel per kategori, sorterat efter returandel |

Ordervärde är antal gånger styckpris. Rabatt är en andel mellan 0 och 1. Returer dras **inte** av från försäljningen. Returandel är antalet returrader delat med antalet unika order inom gruppen. Dubbletter av order-ID tas inte bort. Dessa regler kommer från originalet. Summor avrundas till två decimaler och returandel till tre.

Följande kolumner måste finnas: `order_id`, `order_date`, `customer_id`, `region`, `product_category`, `quantity`, `unit_price`, `discount`, `returned`. Datum och kund-ID används inte i rapportberäkningarna och innehållsvalideras därför inte.

## Validering och avsiktliga skillnader vid felaktiga data

Originalets ersättningsregler bevaras men loggas med WARNING:

- Saknat eller icke-numeriskt antal blir 1; pris blir medianen av numeriska priser; rabatt blir 0. Även `unknown` i rabattkolumnen blir alltså 0.
- Saknad region eller kategori blir `Unknown`. Text trimmas och normaliseras till title case. En grupp som bara består av blanksteg blir en tom sträng, med varning, enligt originalets beteende.
- `true`, `yes`, `1` och `ja`, oberoende av skiftläge och omgivande blanksteg, betyder retur. Övriga värden betyder ingen retur. Saknade eller okända returvärden ger varning.

Nya tydliga fel stoppar körningen vid saknad fil, tom fil/tabell, saknade kolumner, saknat/tomt order-ID, oändliga numeriska värden, antal ≤ 0, negativt pris, rabatt utanför 0–1 eller om inget giltigt pris finns för medianen. Nollpris och full rabatt är tillåtna. Fraktionella positiva antal bevaras. Dessa avgränsade ändringar gäller felaktiga data; den levererade filens fyra rapporter är oförändrade. Ogiltig numerisk text avvisas alltså inte generellt, eftersom det skulle ändra originalets avsiktliga ersättningar och stoppa den medföljande filen.

## Tester och dokumentation

46 pytest-fall passerade. Tester skyddar egna beräkningar, avrundning, gruppering, returlogik, ersättningar, felhantering, import utan sidoeffekter och körning via kommandoraden. Fyra regressionstest jämför hela rapportfiler med normaliserade radslut med originalkörningens rapporter. Kör med de angivna beroendeversionerna för samma CSV-format.

Se `code_review.md` för åtta konkreta förbättringsområden, `verification.md` för körda kommandon och exakt testlista, `checklist.md` för G-kraven och `reflection.md` för reflektionsutkast. Reflektionen beskriver verifierbara tekniska val; läs igenom så att formuleringarna stämmer med din egen förståelse.

Projektet är förberett för att läggas i ett GitHub-repository men har inte publicerats. Inga extra funktioner som webbapp, SQL eller maskininlärning har lagts till.


Slutlig kontroll i Linux: 46 tester passerade. Regressionstesterna normaliserar endast CSV-radslut mellan operativsystem.
