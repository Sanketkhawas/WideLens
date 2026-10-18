"""Generate a realistic SYNTHETIC customer workbook for Nagpur.

    python training/generate_sample_data.py

Writes sample_data/WideLens_Nagpur_Sample.xlsx (+ CSV copies). All customers/sales are random
(seeded) - they are not real people. Area population/rent/competitor numbers are illustrative.
"""
import os
import sys
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from utils.constants import NAGPUR_AREAS  # noqa: E402

rng = np.random.default_rng(2026)
N = 2000

# relative share of customers per locality - existing stores sit in Sitabuldi & Dharampeth
HEAVY = {"Manish Nagar": 9, "Pratap Nagar": 8, "Trimurti Nagar": 8, "Somalwada": 6, "Khamla": 6, "Nandanvan": 6,
         "Sakkardara": 5, "Laxmi Nagar": 5, "Narendra Nagar": 4, "Dharampeth": 7, "Sitabuldi": 7, "Sadar": 4,
         "Ramdaspeth": 4, "Bajaj Nagar": 3, "Medical Square": 3, "Civil Lines": 3, "Dighori": 3, "Ambazari": 2,
         "Mahal": 2, "Itwari": 2, "Gandhibagh": 1.5, "Besa": 2, "Beltarodi": 1.5, "Jaripatka": 1.2, "Mankapur": 1.5,
         "Wadi": 1, "Katol Road": 1, "Kamptee Road": 1.2, "Koradi Road": 0.8, "Hingna": 0.8, "MIHAN": 0.4}
# richer areas spend more
SPEND_MULT = {"Dharampeth": 1.3, "Ramdaspeth": 1.25, "Civil Lines": 1.3, "Sitabuldi": 1.1, "Ambazari": 1.2,
              "Bajaj Nagar": 1.15, "Manish Nagar": 1.1, "Pratap Nagar": 1.05, "Laxmi Nagar": 1.1}
CATS = {"Grocery & Staples": (450, 0.5, 30), "Apparel": (1400, 0.6, 22), "Electronics": (6500, 0.7, 8),
        "Home & Kitchen": (1800, 0.6, 14), "Beauty & Personal Care": (700, 0.5, 16), "Footwear": (1500, 0.5, 10)}
PAY = ["UPI", "Card", "Cash", "Wallet"]
PAYP = [0.52, 0.22, 0.2, 0.06]
SEASON = {1: .95, 2: .9, 3: 1.0, 4: 1.1, 5: 1.1, 6: .9, 7: .9, 8: 1.0, 9: 1.05, 10: 1.35, 11: 1.4, 12: 1.15}

first = ["Aarav", "Vivaan", "Aditya", "Sai", "Arjun", "Rohan", "Pranav", "Omkar", "Tejas", "Yash", "Ketan", "Nilesh", "Amit",
         "Rahul", "Sanjay", "Vikas", "Anil", "Prashant", "Mangesh", "Swapnil", "Priya", "Ananya", "Sneha", "Pooja", "Neha",
         "Kavita", "Shweta", "Rutuja", "Madhuri", "Anjali", "Sayali", "Komal", "Deepa", "Ritu", "Manasi", "Vaishnavi"]
last = ["Deshmukh", "Patil", "Kulkarni", "Joshi", "Wankhede", "Meshram", "Gawande", "Thakre", "Bhoyar", "Raut", "Dhote",
        "Sharma", "Gupta", "Agrawal", "Khandelwal", "Chaudhari", "Nimje", "Pande", "Ingle", "Bawane", "Mishra", "Tiwari",
        "Lokhande", "Zade", "Shende", "Kale", "Dongre", "Borkar"]

areas = pd.DataFrame(NAGPUR_AREAS, columns=["area", "latitude", "longitude", "population", "avg_rent", "competitor_count"])
w = np.array([HEAVY[a] for a in areas["area"]], float)
w /= w.sum()
idx = rng.choice(len(areas), N, p=w)

cust = pd.DataFrame({"customer_id": [f"C{1000 + i}" for i in range(N)]})
cust["customer_name"] = [f"{rng.choice(first)} {rng.choice(last)}" for _ in range(N)]
cust["age"] = np.clip(rng.normal(34, 11, N), 18, 75).round().astype(int)
cust["gender"] = rng.choice(["Male", "Female"], N, p=[0.46, 0.54])
cust["area"] = areas["area"].values[idx]
cust["city"] = "Nagpur"
cust["latitude"] = areas["latitude"].values[idx] + rng.normal(0, 0.010, N)
cust["longitude"] = areas["longitude"].values[idx] + rng.normal(0, 0.010, N)

months = pd.period_range("2025-01", "2026-09", freq="M")
mw = np.array([SEASON[p.month] * (1 + 0.018 * i) for i, p in enumerate(months)])
mw /= mw.sum()
catp = np.array([v[2] for v in CATS.values()], float)
catp /= catp.sum()
rows = []
sid = 1
for i, cr in cust.iterrows():
    n = 1 + rng.poisson(max(0.5, 5.0 * rng.gamma(2, 0.5) * (1.1 if cr["age"] < 45 else 0.85)))
    mult = SPEND_MULT.get(cr["area"], 1.0)
    for _ in range(n):
        cat = rng.choice(list(CATS), p=catp)
        base, sig, _w = CATS[cat]
        qty = int(rng.integers(1, 4)) if cat in ("Grocery & Staples", "Beauty & Personal Care") else 1
        amt = float(np.round(rng.lognormal(np.log(base * mult), sig) * qty, 0))
        mth = months[rng.choice(len(months), p=mw)]
        day = int(rng.integers(1, mth.days_in_month + 1))
        rows.append((sid, cr["customer_id"], cat, qty, amt, pd.Timestamp(mth.year, mth.month, day), rng.choice(PAY, p=PAYP)))
        sid += 1
sales = pd.DataFrame(rows, columns=["sale_id", "customer_id", "product", "quantity", "amount", "sale_date", "payment_method"])
agg = sales.groupby("customer_id")["amount"].agg(["count", "sum"])
cust["purchase_frequency"] = cust["customer_id"].map(agg["count"]).astype(int)
cust["total_spent"] = cust["customer_id"].map(agg["sum"]).round(0)

# a few realistically messy rows so the cleaner has something to do
bad = rng.choice(N, 14, replace=False)
cust.loc[bad[:8], ["latitude", "longitude"]] = np.nan
cust.loc[bad[8:11], "area"] = cust.loc[bad[8:11], "area"].str.upper() + " "
cust.loc[bad[11:], "area"] = ""

stores = pd.DataFrame([
    ("WideStore Sitabuldi", "Sitabuldi", 21.1458, 79.0882),
    ("WideStore Dharampeth", "Dharampeth", 21.1380, 79.0650),
], columns=["store_name", "area", "latitude", "longitude"])

readme = pd.DataFrame({"WideLens upload template": [
    "Sheet 'Customers' (required): customer_id, customer_name, age, gender, area, city, latitude, longitude, purchase_frequency, total_spent",
    "Sheet 'Sales' (optional, enables trends + forecast): sale_id, customer_id, product, quantity, amount, sale_date, payment_method",
    "Sheet 'Stores' (optional): your EXISTING stores - store_name, area, latitude, longitude",
    "Sheet 'Areas' (optional): override locality data - area, latitude, longitude, population, avg_rent (Rs/sq ft/month), competitor_count",
    "Missing latitude/longitude are filled from the area; missing area is inferred from coordinates.",
    "SAMPLE FILE: all customers and sales are randomly generated; area population/rent/competitor values are illustrative.",
]})

os.makedirs(os.path.join(ROOT, "sample_data"), exist_ok=True)
xl = os.path.join(ROOT, "sample_data", "WideLens_Nagpur_Sample.xlsx")
with pd.ExcelWriter(xl, engine="openpyxl", datetime_format="YYYY-MM-DD") as xw:
    readme.to_excel(xw, sheet_name="README", index=False)
    cust.to_excel(xw, sheet_name="Customers", index=False)
    sales.to_excel(xw, sheet_name="Sales", index=False)
    stores.to_excel(xw, sheet_name="Stores", index=False)
    areas.to_excel(xw, sheet_name="Areas", index=False)
    for ws in xw.book.worksheets:
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = min(60, max(12, max(len(str(c.value or "")) for c in col[:50]) + 2))
        ws.freeze_panes = "A2"
cust.to_csv(os.path.join(ROOT, "sample_data", "sample_customers.csv"), index=False)
sales.to_csv(os.path.join(ROOT, "sample_data", "sample_sales.csv"), index=False)
stores.to_csv(os.path.join(ROOT, "sample_data", "sample_locations.csv"), index=False)
areas.to_csv(os.path.join(ROOT, "sample_data", "sample_demographics.csv"), index=False)
print(f"customers={len(cust)} sales={len(sales)} -> {xl}")
