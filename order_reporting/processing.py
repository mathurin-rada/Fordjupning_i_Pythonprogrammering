import pandas as pd


def calculate_order_values(data: pd.DataFrame) -> pd.DataFrame:
    """Returer ingår i försäljningen, precis som i originalet."""
    result = data.copy()
    result["order_value"] = result["quantity"] * result["unit_price"]
    result["discounted_value"] = result["order_value"] * (1 - result["discount"])
    return result


def summarize_orders(data: pd.DataFrame, group: str, include_sales: bool = True) -> pd.DataFrame:
    aggregations = {"order_count": ("order_id", "nunique")}
    if include_sales:
        aggregations["total_sales"] = ("discounted_value", "sum")
    aggregations["returns"] = ("returned", "sum")
    result = data.groupby(group, as_index=False).agg(**aggregations)
    if include_sales:
        result["total_sales"] = result["total_sales"].round(2)
    result["return_rate"] = (result["returns"] / result["order_count"]).round(3)
    sort_column = "total_sales" if include_sales else "return_rate"
    return result.sort_values(sort_column, ascending=False).reset_index(drop=True)
