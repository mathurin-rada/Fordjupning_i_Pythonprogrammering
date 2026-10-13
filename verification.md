# Körprotokoll och verifiering

Datum: 2026-10-13. Windows, Python 3.12.14, pandas 3.0.1, pytest 8.3.5.

## Inventering och originalkörning

Indata var `C:/Users/new_f/Downloads/order_report_project.zip`. Arkivet listades före uppackning med .NET `System.IO.Compression.ZipFile`. Det innehöll `order_report.py`, `data/orders.csv` och katalogposter, inklusive en tom `output/`. All Pythonkod och hela CSV-filen lästes före ändring. Inga instruktioner eller andra projektfiler fanns i arkivet.

Följande kommandon kördes från arbetsmappen, som är två nivåer ovanför det levererade projektet:

```powershell
Expand-Archive -LiteralPath 'C:\Users\new_f\Downloads\order_report_project.zip' -DestinationPath 'work\original'
Get-Content -LiteralPath 'work\original\order_report_project\order_report.py' -Raw
Get-Content -LiteralPath 'work\original\order_report_project\data\orders.csv' -Raw
python --version
```

Det sista kommandot misslyckades eftersom `python` inte fanns i PATH. Den tillgängliga lokala runtimen identifierades och användes därefter. Från `work/original/order_report_project` kördes:

```powershell
& 'C:\Users\new_f\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "import sys,pandas,pytest; print(sys.version); print('pandas', pandas.__version__); print('pytest', pytest.__version__)"
& 'C:\Users\new_f\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' order_report.py
Get-Content output\*.csv
```

Versionskontrollen misslyckades eftersom pytest saknades. Originalprogrammet kördes ändå separat och lyckades. Det skrev startmeddelande, 80 inlästa rader, fyra sparade filnamn och `Klart`. Svenska konsoltecken visades fel i denna första utskrift. Rapportfilerna skapades korrekt. Resultaten redovisas i `code_review.md`, och alla originalrapporter sparades i `tests/baseline/`.

## Testmiljö och första refaktorerade körningen

Från arbetsmappen:

```powershell
& 'C:\Users\new_f\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv --system-site-packages work\venv
& '.\work\venv\Scripts\python.exe' -m pip install pytest
& '.\work\venv\Scripts\python.exe' -m pip install pytest==8.3.5
```

Det första installationsförsöket stoppades av nätverksbegränsningen. Det andra kördes med godkänd nätverksåtkomst och lyckades. Testmiljön är separat under `work/venv` och använder den befintliga pandas-installationen. Ingen ren installation av samtliga beroenden i en tom miljö genomfördes. `requirements.txt` anger de två direktberoendens faktiskt verifierade versioner.

Från det levererade projektets rot kördes:

```powershell
& '..\..\work\venv\Scripts\python.exe' order_report.py
```

Körningen lyckades och skapade fyra rapporter. Logging visade 80 rader, en saknad region, ett ersatt antal, ett ersatt pris med median 499.0, två ersatta rabatter och saknat returvärde. Därefter loggades lyckad validering, fyra skapade rapporter, varje sparad fil och `Klart`.

En versionskontroll med fel relativ sökväg (`.\work\venv\Scripts\python.exe` från projektroten) misslyckades. Den korrigerade kontrollen kördes från arbetsmappen:

```powershell
& '.\work\venv\Scripts\python.exe' -c "import sys,pandas; print(sys.version); print('pandas',pandas.__version__)"
Get-FileHash work\original\order_report_project\output\*.csv
Get-FileHash outputs\order_report_project\output\*.csv
```

Python 3.12.14 och pandas 3.0.1 bekräftades. SHA-256-värdena för alla fyra rapporterna överensstämde. Senare pytest-fall jämförde också innehållet efter normalisering av radslut. Det finns inga skillnader i rapportinnehåll, kolumnordning, radordning, avrundning eller CSV-format i den verifierade miljön.

## Automatiska tester

Efter att testerna lagts till kördes följande från projektroten:

```powershell
& '..\..\work\venv\Scripts\python.exe' -m pytest -v --tb=short
```

Faktiskt resultat: **46 passed in 3.89s**, exitkod **0**. Inga tester misslyckades eller hoppades över. Ingen programkod ändrades efter denna lyckade testkörning; därefter tillkom dokumentation och paketering.

Samtliga passerade testfall (parametrar anges inom hakparentes):

```text
tests/test_integration.py
  test_reports_match_original_content[overview.csv]
  test_reports_match_original_content[sales_by_category.csv]
  test_reports_match_original_content[sales_by_region.csv]
  test_reports_match_original_content[returns_by_category.csv]
  test_missing_file
  test_empty_file
  test_header_only_file
  test_malformed_csv
  test_main_returns_failure_and_logs
  test_output_path_is_a_file
  test_cli_from_another_directory
  test_import_has_no_side_effects

tests/test_processing.py
  test_order_values_discounts_and_no_input_mutation
  test_overview_includes_returned_sales
  test_sales_summaries[sales_by_category.csv-product_category-labels0]
  test_sales_summaries[sales_by_region.csv-region-labels1]
  test_return_report_sorted_by_rate
  test_duplicate_order_ids_count_once_but_returns_count_rows
  test_full_discount_and_free_product
  test_rounding_happens_after_sum

tests/test_validation.py
  test_missing_columns
  test_empty_data
  test_original_numeric_fallbacks_are_logged[None]
  test_original_numeric_fallbacks_are_logged[invalid]
  test_unreasonable_numbers_rejected[quantity-0-quantity]
  test_unreasonable_numbers_rejected[quantity--1-quantity]
  test_unreasonable_numbers_rejected[unit_price--1-unit_price]
  test_unreasonable_numbers_rejected[discount--0.1-discount]
  test_unreasonable_numbers_rejected[discount-1.1-discount]
  test_unreasonable_numbers_rejected[quantity-inf-oändliga]
  test_unreasonable_numbers_rejected[unit_price--inf-oändliga]
  test_unreasonable_numbers_rejected[discount-inf-oändliga]
  test_no_price_median_available
  test_missing_order_id[None]
  test_missing_order_id[ ]
  test_missing_and_inconsistent_labels
  test_return_tokens[true-True]
  test_return_tokens[ YES -True]
  test_return_tokens[1-True]
  test_return_tokens[Ja-True]
  test_return_tokens[false-False]
  test_return_tokens[no-False]
  test_return_tokens[0-False]
  test_return_tokens[nej-False]
  test_return_tokens[None-False]
  test_return_tokens[unknown-False]
```

Pytest visade `ä` som `\xe4` i de tre parametriserade namnen med ”oändliga”; ovan är dessa återgivna med läsbara svenska tecken.

## Skapade och ändrade filer

- **Refaktorerad:** `order_report.py`, ersatt toppnivåflöde med startpunkt och anrop till separata moduler.
- **Nya:** samtliga sex filer i `order_reporting/` (inklusive `__init__.py`), fyra Pythonfiler i `tests/`, `requirements.txt`, `.gitignore`, `README.md`, `code_review.md`, `reflection.md`, `verification.md`, `checklist.md`.
- **Oförändrade kopior:** `data/orders.csv` och `original/order_report.py`. Källarkivet i Downloads ändrades inte.
- **Jämförelseunderlag:** fyra CSV-filer i `tests/baseline/` från originalkörningen.
- **Genererade resultat:** fyra CSV-filer i `output/` från refaktoreringen, identiska med jämförelseunderlaget.
- **Leverans:** `order_report_project_refactored.zip` innehåller projektmappen utan virtuella miljöer, Python-cache eller pytest-cache.

Projektstrukturen och vanliga installations-/körkommandon finns i `README.md`. De maskinspecifika sökvägarna ovan är endast ett protokoll över denna körning, inte ett krav för att använda projektet.

## Begränsningar och skillnader

De nya stoppreglerna för felaktig data är dokumenterade i README. Dessa ändrar beteendet för exempelvis negativa priser, men inte för levererad data. Datum och kund-ID valideras endast som obligatoriska kolumner. Sparandet av flera rapporter är inte atomiskt. Testerna verifierar den dokumenterade miljön, inte alla möjliga operativsystem eller beroendeversioner. Inga kvarvarande fel observerades i de genomförda testerna.


## Slutlig kontroll i separat Linux-miljö

Efter leveransen justerades fyra regressionstester så att enbart radslut (`CRLF`/`LF`) normaliseras före jämförelse. Övriga bytes, kolumnordning och beräknade värden jämförs oförändrade. `python -m pytest -q` kördes i Linux och gav **46 passed in 7.49s**. Ingen produktionskod ändrades. Reflektionen redigerades till en sammanhängande teknisk text utan platshållare.
