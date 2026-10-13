import logging
import math

import pandas as pd

logger = logging.getLogger(__name__)
REQUIRED_COLUMNS = {
    "order_id", "order_date", "customer_id", "region", "product_category",
    "quantity", "unit_price", "discount", "returned",
}


class DataValidationError(ValueError):
    """Indata kan inte användas för en tillförlitlig rapport."""


def validate_and_clean(data: pd.DataFrame) -> pd.DataFrame:
    """Bevara originalets ersättningsregler och varna när de används."""
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise DataValidationError(f"Obligatoriska kolumner saknas: {', '.join(sorted(missing))}")
    if data.empty:
        raise DataValidationError("Datafilen innehåller inga orderrader.")
    data = data.copy()
    if data["order_id"].isna().any() or data["order_id"].astype(str).str.strip().eq("").any():
        raise DataValidationError("order_id får inte saknas eller vara tomt.")
    for column in ("region", "product_category"):
        if data[column].isna().any():
            logger.warning("%s: %d saknade värden ersätts med Unknown", column, data[column].isna().sum())
        data[column] = data[column].fillna("Unknown").astype(str).str.strip().str.title()
        if data[column].eq("").any():
            logger.warning("%s innehåller tomma grupper; bevaras enligt originalet", column)
    for column, default in (("quantity", 1), ("unit_price", None), ("discount", 0)):
        numeric = pd.to_numeric(data[column], errors="coerce")
        if numeric.dropna().map(lambda value: not math.isfinite(value)).any():
            raise DataValidationError(f"{column} innehåller oändliga värden.")
        if column == "unit_price":
            if numeric.notna().sum() == 0:
                raise DataValidationError("unit_price saknar giltiga priser; median kan inte beräknas.")
            default = numeric.median()
        if numeric.isna().any():
            logger.warning("%s: %d saknade/ogiltiga värden ersätts med %s", column, numeric.isna().sum(), default)
        data[column] = numeric.fillna(default)
    if (data["quantity"] <= 0).any():
        raise DataValidationError("quantity måste vara större än 0.")
    if (data["unit_price"] < 0).any():
        raise DataValidationError("unit_price får inte vara negativt.")
    if not data["discount"].between(0, 1).all():
        raise DataValidationError("discount måste ligga mellan 0 och 1.")
    returned = data["returned"].fillna("false").astype(str).str.strip().str.lower()
    known = {"true", "yes", "1", "ja", "false", "no", "0", "nej"}
    if data["returned"].isna().any() or (~returned.isin(known)).any():
        logger.warning("Saknade/okända returvärden tolkas som false enligt originalet")
    data["returned"] = returned.isin(["true", "yes", "1", "ja"])
    logger.info("Validerade %d rader", len(data))
    return data
