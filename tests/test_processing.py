import pytest

from order_reporting.processing import calculate_order_values
from order_reporting.reporting import create_reports
from order_reporting.validation import validate_and_clean


def test_order_values_discounts_and_no_input_mutation(orders):
    cleaned = validate_and_clean(orders)
    result = calculate_order_values(cleaned)
    assert result["order_value"].tolist() == [200, 50, 60]
    assert result["discounted_value"].tolist() == [180, 50, 30]
    assert "order_value" not in cleaned
    assert orders.loc[0, "region"] == " north "


def test_overview_includes_returned_sales(orders):
    reports = create_reports(calculate_order_values(validate_and_clean(orders)))
    overview = reports["overview.csv"].set_index("metric")["value"].to_dict()
    assert overview == {"total_sales": 260, "order_count": 3, "return_count": 2}


@pytest.mark.parametrize("filename,group,labels", [
    ("sales_by_category.csv", "product_category", ["Books", "Sports"]),
    ("sales_by_region.csv", "region", ["North", "South"]),
])
def test_sales_summaries(orders, filename, group, labels):
    report = create_reports(calculate_order_values(validate_and_clean(orders)))[filename]
    assert report.to_dict("list") == {
        group: labels, "order_count": [2, 1], "total_sales": [230, 30],
        "returns": [1, 1], "return_rate": [0.5, 1.0],
    }


def test_return_report_sorted_by_rate(orders):
    report = create_reports(calculate_order_values(validate_and_clean(orders)))["returns_by_category.csv"]
    assert report.to_dict("list") == {
        "product_category": ["Sports", "Books"], "order_count": [1, 2],
        "returns": [1, 1], "return_rate": [1.0, 0.5],
    }


def test_duplicate_order_ids_count_once_but_returns_count_rows(orders):
    orders.loc[1, "order_id"] = "A"
    orders.loc[1, "returned"] = "true"
    reports = create_reports(calculate_order_values(validate_and_clean(orders)))
    books = reports["sales_by_category.csv"].iloc[0]
    assert books["order_count"] == 1
    assert books["returns"] == 2
    assert books["return_rate"] == 2.0


def test_full_discount_and_free_product(orders):
    orders.loc[0, "discount"] = 1
    orders.loc[1, "unit_price"] = 0
    result = calculate_order_values(validate_and_clean(orders))
    assert result["discounted_value"].tolist() == [0, 0, 30]


def test_rounding_happens_after_sum(orders):
    orders["quantity"] = 1
    orders["unit_price"] = 0.3333
    orders["discount"] = 0
    orders["product_category"] = "Books"
    orders["returned"] = ["true", "false", "false"]
    reports = create_reports(calculate_order_values(validate_and_clean(orders)))
    row = reports["sales_by_category.csv"].iloc[0]
    assert row["total_sales"] == 1.0
    assert row["return_rate"] == 0.333
