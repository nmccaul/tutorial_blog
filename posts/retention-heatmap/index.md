---
title: "Do Your Customers Come Back? Building a Retention Heatmap in Seaborn"
description: "Turn a list of orders into a cohort retention heatmap, and learn to read it like a product manager."
author: "Nathan McCauley"
date: "2026-10-16"
categories: [visualization, seaborn, pandas, product]
image: images/retention_heatmap.png
draft: true
---

<!--
WRITING NOTES (delete these comments before publishing; set draft: false above)
- Target: 700–1,100 words of prose. Code blocks and tables don't count.
- Each section has a prompt in an HTML comment. Replace each prompt with your own writing.
- Every number in this file comes from running retention.py. Re-run it if you change anything.
-->

## Why retention matters

<!--
PROMPT (~150 words):
- Hook: a store's order count can grow while most new customers never come back. Totals hide that; retention shows it.
- Define a cohort: customers grouped by the month of their first order.
- Explain the formula below in plain words (what's on top, what's on the bottom).
- Tell the reader what they'll be able to do by the end.
-->

$$
\text{Retention}_{c,\,m} = \frac{\text{customers in cohort } c \text{ who order } m \text{ months after their first order}}{\text{customers in cohort } c}
$$

## The data

<!--
PROMPT (~80 words):
- Where the data comes from (link the UCI dataset descriptively) and that it was trimmed to one row per completed order, Dec 2010 – Nov 2011.
- 17,758 orders from 4,298 customers.
- The same steps work on any data with an ID and a date.
-->

```python
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

url = "https://raw.githubusercontent.com/nmccaul/tutorial_blog/main/posts/retention-heatmap/data/orders.csv"
orders = pd.read_csv(url, parse_dates=["order_date"])
orders.head()
```

| customer_id | order_date |
|------------:|:-----------|
| 17850 | 2010-12-01 |
| 17850 | 2010-12-01 |
| 13047 | 2010-12-01 |
| 13047 | 2010-12-01 |
| 13047 | 2010-12-01 |

## Step 1: Build the cohort table

### Find each customer's cohort

<!-- PROMPT: what transform("min") does here, and why transform instead of agg (it keeps one value per row). -->

```python
orders["order_month"] = orders["order_date"].dt.to_period("M")
orders["cohort"] = orders.groupby("customer_id")["order_month"].transform("min")
```

### Count months since the first order

<!-- PROMPT: subtracting two monthly periods gives an offset; .n turns it into a plain number. -->

```python
orders["months_since_first"] = (orders["order_month"] - orders["cohort"]).apply(
    lambda offset: offset.n
)
```

### Turn counts into percentages

<!-- PROMPT: nunique counts each customer once per month; unstack makes months into columns; dividing by column 0 turns counts into shares. -->

```python
active = (
    orders.groupby(["cohort", "months_since_first"])["customer_id"]
    .nunique()
    .unstack()
)
cohort_size = active[0]
retention = active.div(cohort_size, axis=0)
```

The top-left corner of the table looks like this:

| cohort  | 0    | 1   | 2   | 3   |
|:--------|:-----|:----|:----|:----|
| 2010-12 | 100% | 37% | 32% | 38% |
| 2011-01 | 100% | 22% | 27% | 23% |
| 2011-02 | 100% | 19% | 19% | 28% |
| 2011-03 | 100% | 15% | 25% | 20% |

<!-- PROMPT: the full table is 12 x 12 = 144 percentages. Hard to scan, which is why we plot it. -->

## Step 2: Plot it with `sns.heatmap`

<!--
PROMPT (~220 words), the core of the post. Walk through each argument:
- annot=True, fmt=".0%": percentages printed in each cell
- cmap="Blues": a sequential palette (darker = more retained); why sequential fits low-to-high data
- vmin=0, vmax=0.5: without a cap, month 0 (always 100%) uses up the whole color range and every other cell looks the same pale shade
- title and axis labels that say what the reader is looking at
Optional: show the bare sns.heatmap(retention) first so readers see the before/after.
-->

```python
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
plt.show()
```

![Heatmap of monthly customer retention for 12 cohorts from December 2010 to November 2011. Month 0 is 100% for every cohort. The December 2010 cohort stays darker, around 35 to 40% each month, while later cohorts are lighter, mostly 15 to 30%. The bottom-right triangle is empty because newer cohorts have fewer months of data.](images/retention_heatmap.png)

## Step 3: Read the heatmap

<!--
PROMPT (~200 words). Use these (all from the figure):
- Across a row: one cohort over time.
- Down a column: compare cohorts at the same age. Dec 2010 stays ~35–40%; later cohorts ~20–25%.
- Diagonals: same calendar month. The Nov 2011 diagonal is darker across most cohorts: holiday shopping, not loyalty.
- Empty triangle: newer cohorts haven't had time yet. Not missing data.
- Caution: data starts Dec 2010, so that cohort includes long-time customers whose real first order was earlier.
Consider a bulleted list here.
-->

## Try it yourself

<!--
PROMPT (~120 words):
- Recap the steps as a short list: cohort -> months since first order -> retention table -> heatmap -> read rows, columns, diagonals.
- Concrete next step: run the code on your own data with an ID and a date, or switch to weekly cohorts with .dt.to_period("W").
- Descriptive links (keep or edit):
  - [seaborn's heatmap documentation](https://seaborn.pydata.org/generated/seaborn.heatmap.html)
  - [pandas guide to groupby](https://pandas.pydata.org/docs/user_guide/groupby.html)
  - [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail)
- Mention that the full code is in this post's folder on GitHub (retention.py).
-->
