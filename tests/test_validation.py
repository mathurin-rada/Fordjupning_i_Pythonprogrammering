import logging

import pytest

from order_reporting.validation import DataValidationError, validate_and_clean


def test_missing_columns(orders):
    with pytest.raises(DataValidationError, match="discount, quantity"):
        validate_and_clean(orders.drop(columns=["quantity", "discount"]))


def test_empty_data(orders):
    with pytest.raises(DataValidationError, match="inga orderrader"):
        validate_and_clean(orders.iloc[:0])


@pytest.mark.parametrize("value", [None, "invalid"])
def test_original_numeric_fallbacks_are_logged(orders, caplog, value):
    for column in ("quantity", "unit_price", "discount"):
        orders[column] = orders[column].astype(object)
        orders.loc[0, column] = value
    with caplog.at_level(logging.WARNING):
        result = validate_and_clean(orders)
    assert result.loc[0, "quantity"] == 1
    assert result.loc[0, "unit_price"] == 35
    assert result.loc[0, "discount"] == 0
    for column in ("quantity", "unit_price", "discount"):
        assert column in caplog.text


@pytest.mark.parametrize("column,value,message", [
    ("quantity", 0, "quantity"), ("quantity", -1, "quantity"),
    ("unit_price", -1, "unit_price"), ("discount", -0.1, "discount"),
    ("discount", 1.1, "discount"), ("quantity", float("inf"), "oändliga"),
    ("unit_price", float("-inf"), "oändliga"), ("discount", float("inf"), "oändliga"),
])
def test_unreasonable_numbers_rejected(orders, column, value, message):
    orders[column] = orders[column].astype(object)
    orders.loc[0, column] = value
    with pytest.raises(DataValidationError, match=message):
        validate_and_clean(orders)


def test_no_price_median_available(orders):
    orders["unit_price"] = "invalid"
    with pytest.raises(DataValidationError, match="median"):
        validate_and_clean(orders)


@pytest.mark.parametrize("value", [None, " "])
def test_missing_order_id(orders, value):
    orders.loc[0, "order_id"] = value
    with pytest.raises(DataValidationError, match="order_id"):
        validate_and_clean(orders)


def test_missing_and_inconsistent_labels(orders, caplog):
    orders.loc[0, "region"] = None
    orders.loc[0, "product_category"] = None
    orders.loc[1, "region"] = " SOUTH "
    orders.loc[2, "region"] = " "
    result = validate_and_clean(orders)
    assert result["region"].tolist() == ["Unknown", "South", ""]
    assert result.loc[0, "product_category"] == "Unknown"
    assert "tomma grupper" in caplog.text


@pytest.mark.parametrize("value,expected", [
    ("true", True), (" YES ", True), ("1", True), ("Ja", True),
    ("false", False), ("no", False), ("0", False), ("nej", False),
    (None, False), ("unknown", False),
])
def test_return_tokens(orders, value, expected, caplog):
    orders.loc[0, "returned"] = value
    assert bool(validate_and_clean(orders).loc[0, "returned"]) is expected
    if value in (None, "unknown"):
        assert "returvärden" in caplog.text
