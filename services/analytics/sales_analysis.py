import pandas as pd


def monthly(sales):
    m = sales.set_index("sale_date")["amount"].resample("MS").agg(["sum", "count"])
    return m.rename(columns={"sum": "revenue", "count": "orders"})


def by_category(sales):
    g = sales.groupby("product")["amount"].agg(["sum", "count"]).sort_values("sum", ascending=False)
    return g.rename(columns={"sum": "revenue", "count": "orders"})


def by_payment(sales):
    return sales.groupby("payment_method")["amount"].sum().sort_values(ascending=False)


def category_by_area(sales, customers, top_areas):
    j = sales.merge(customers[["customer_id", "area"]], on="customer_id")
    j = j[j["area"].isin(top_areas)]
    return j.pivot_table(index="area", columns="product", values="amount", aggfunc="sum", fill_value=0)
