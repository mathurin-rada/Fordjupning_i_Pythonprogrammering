# Slutkontroll mot angivna G-krav

Bedömningen avser kraven i den inklistrade instruktionen. En separat officiell bedömningsmatris har inte tillhandahållits.

| Krav | Status | Fil och verifiering |
| --- | --- | --- |
| Inventera och läsa originalet före ändring | UPPFYLLT | ZIP: en Pythonfil, orders.csv och tom output-katalog; båda filerna lästa; `code_review.md` |
| Köra och dokumentera originalet | UPPFYLLT | `original/order_report.py`, `tests/baseline/`, `code_review.md`, `verification.md` |
| Minst fem konkreta granskningsområden | UPPFYLLT | Åtta områden i `code_review.md`, alla med Observation, Konsekvens, Förslag och kodhänvisning |
| Tydlig kod och separata ansvar | UPPFYLLT | `order_reporting/`: filhantering, validering, bearbetning och rapportering |
| Minska duplicering och förbättra namn | UPPFYLLT | `processing.summarize_orders`, `reporting.create_reports` |
| Explicita importer utan sys.path-hack | UPPFYLLT | Alla nya moduler; CLI- och importtester passerade |
| Tydlig startpunkt utan importeffekter | UPPFYLLT | `order_report.main`, startpunktsskydd och `test_import_has_no_side_effects` |
| Central logging och modul-loggers | UPPFYLLT | `order_report.py`, `file_io.py`, `validation.py`, `reporting.py`; verklig körning loggade rader, validering, varningar och fyra sparade rapporter |
| Relevant klass/dataclass med motivering | UPPFYLLT | `config.ReportConfig`, motiverad i README och reflektion |
| Saknad fil, saknade kolumner och tom data | UPPFYLLT | `file_io.py`, `validation.py`; motsvarande tester passerade |
| Ogiltiga tal, orimliga och inkonsekventa värden | UPPFYLLT | Tester i `test_validation.py`; originalets ersättningar loggas, nya stoppregler dokumenteras i README |
| Specifika fel utan att dölja programmeringsfel | UPPFYLLT | `DataValidationError`; avgränsad catch i `main`; test för felkod och fellogg |
| Bevara centrala beräkningar och rapporter | UPPFYLLT | Fyra innehållsjämförelser mot originalrapporter passerade; oförändrad orders.csv |
| pytest med kontrollerade normalfall och edge cases | UPPFYLLT | 46 passerade fall i tre testmoduler; exakt lista i `verification.md` |
| Installation, beroenden, körning och filstruktur | UPPFYLLT | `README.md`, `requirements.txt`; använd Python 3.11+ |
| Kort reflektion baserad på faktiskt arbete | UPPFYLLT | `reflection.md` besvarar sju frågor; tekniska avvägningar beskrivna |
| Komplett körbart projekt för GitHub | UPPFYLLT | README, kod, data, tester, beroenden, .gitignore och exempelrapporter finns; ingen publicering utförd |
| Redovisa kommandon, testresultat och ändrade filer | UPPFYLLT | `verification.md` och README:s struktur |

Inga kvarvarande testfel. Studenten bör kunna förklara lösningen och reflektionen vid frågor.
