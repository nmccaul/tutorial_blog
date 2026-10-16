"""Build data/orders.csv from the UCI Online Retail dataset.

Keeps one row per completed order (customer_id, order_date):
drops guest checkouts (no CustomerID), cancelled invoices (InvoiceNo
starting with "C"), and December 2011, which is only partly covered.

Source: https://archive.ics.uci.edu/dataset/352/online+retail
"""

import io
import urllib.request
import zipfile

import pandas as pd

URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"

with urllib.request.urlopen(URL) as response:
    archive = zipfile.ZipFile(io.BytesIO(response.read()))

raw = pd.read_excel(
    archive.open("Online Retail.xlsx"),
    usecols=["InvoiceNo", "CustomerID", "InvoiceDate"],
)

orders = (
    raw.dropna(subset=["CustomerID"])
    .loc[lambda d: ~d["InvoiceNo"].astype(str).str.startswith("C")]
    .loc[lambda d: d["InvoiceDate"] < "2011-12-01"]
    .drop_duplicates("InvoiceNo")
    .assign(
        customer_id=lambda d: d["CustomerID"].astype(int),
        order_date=lambda d: d["InvoiceDate"].dt.date,
    )[["customer_id", "order_date"]]
)

orders.to_csv("data/orders.csv", index=False)
print(f"Wrote {len(orders):,} orders from {orders['customer_id'].nunique():,} customers")
