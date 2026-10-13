import argparse
import logging
from pathlib import Path

from order_reporting.config import ReportConfig
from order_reporting.file_io import read_orders, save_reports
from order_reporting.processing import calculate_order_values
from order_reporting.reporting import create_reports
from order_reporting.validation import DataValidationError, validate_and_clean

logger = logging.getLogger(__name__)


def run_report(config: ReportConfig) -> None:
    data = read_orders(config.input_file)
    cleaned = validate_and_clean(data)
    calculated = calculate_order_values(cleaned)
    save_reports(create_reports(calculated), config.output_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Skapa orderrapporter från CSV.")
    parser.add_argument("--input", type=Path, default=Path("data/orders.csv"))
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logger.info("Startar orderrapport")
    try:
        run_report(ReportConfig(args.input, args.output))
    except (OSError, DataValidationError, UnicodeError) as error:
        logger.error("Kunde inte skapa rapporterna: %s", error)
        return 1
    logger.info("Klart")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
