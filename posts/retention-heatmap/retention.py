"""Build a monthly cohort retention table and plot it as a seaborn heatmap.

The code here matches the code blocks in post.md, so the figure and tables
in the post come from running this file.
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Load one row per order
orders = pd.read_csv("data/orders.csv", parse_dates=["order_date"])

# Step 1: each customer's cohort is the month of their first order
orders["order_month"] = orders["order_date"].dt.to_period("M")
orders["cohort"] = orders.groupby("customer_id")["order_month"].transform("min")

# Step 2: how many months after their first order each order happened
orders["months_since_first"] = (orders["order_month"] - orders["cohort"]).apply(
    lambda offset: offset.n
)

# Step 3: count active customers, then divide by each cohort's size
active = (
    orders.groupby(["cohort", "months_since_first"])["customer_id"]
    .nunique()
    .unstack()
)
cohort_size = active[0]
retention = active.div(cohort_size, axis=0)

# Step 4: plot the heatmap
fig, ax = plt.subplots(figsize=(11, 7))
sns.heatmap(
    retention,
    annot=True,
    fmt=".0%",
    cmap="Blues",
    vmin=0,
    vmax=0.5,
    cbar_kws={"label": "Share of cohort ordering again"},
    ax=ax,
)
ax.set_title("Monthly retention by first-order cohort")
ax.set_xlabel("Months since first order")
ax.set_ylabel("Cohort (month of first order)")
fig.tight_layout()
fig.savefig("images/retention_heatmap.png", dpi=150)

# Tables and numbers for the post
print(orders.head().to_markdown(index=False))
print()
print(retention.iloc[:4, :4].map("{:.0%}".format).to_markdown())
print()
print(cohort_size.to_string())
