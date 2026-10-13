import logging

import pandas as pd

from order_reporting.processing import summarize_orders

logger = logging.getLogger(__name__)


def create_reports(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    overview = pd.DataFrame({
        "metric": ["total_sales", "order_count", "return_count"],
        "value": [round(data["discounted_value"].sum(), 2),
                  data["order_id"].nunique(), int(data["returned"].sum())],
    })
    reports = {
        "overview.csv": overview,
        "sales_by_category.csv": summarize_orders(data, "product_category"),
        "sales_by_region.csv": summarize_orders(data, "region"),
        "returns_by_category.csv": summarize_orders(data, "product_category", include_sales=False),
    }
    logger.info("Skapade %d rapporter", len(reports))
    return reports
