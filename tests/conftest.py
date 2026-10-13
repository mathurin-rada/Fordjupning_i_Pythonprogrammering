import pandas as pd
import pytest


@pytest.fixture
def orders():
    return pd.DataFrame({
        "order_id": ["A", "B", "C"],
        "order_date": ["2026-01-01"] * 3,
        "customer_id": ["X", "Y", "Z"],
        "region": [" north ", "North", "South"],
        "product_category": ["books", "Books", "Sports"],
        "quantity": [2, 1, 3],
        "unit_price": [100, 50, 20],
        "discount": [0.1, 0, 0.5],
        "returned": ["yes", "false", "ja"],
    })
