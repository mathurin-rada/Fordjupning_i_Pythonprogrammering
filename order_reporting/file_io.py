import logging
from pathlib import Path

import pandas as pd

from order_reporting.validation import DataValidationError

logger = logging.getLogger(__name__)


def read_orders(path: Path) -> pd.DataFrame:
    logger.info("Läser %s", path)
    try:
        data = pd.read_csv(path)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"CSV-filen saknas: {path}") from error
    except pd.errors.EmptyDataError as error:
        raise DataValidationError(f"CSV-filen är tom: {path}") from error
    except pd.errors.ParserError as error:
        raise DataValidationError(f"CSV-filen har felaktig struktur: {path}") from error
    logger.info("Läste in %d rader", len(data))
    return data


def save_reports(reports: dict[str, pd.DataFrame], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, report in reports.items():
        path = output_dir / filename
        report.to_csv(path, index=False)
        logger.info("Sparade %s", path)
