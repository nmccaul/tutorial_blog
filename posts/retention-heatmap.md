---
title: "Do Your Customers Come Back? Building a Retention Heatmap in Seaborn"
---

# Do Your Customers Come Back? Building a Retention Heatmap in Seaborn

*Nathan McCauley · STAT 386 · October 2026*

Imagine you're a product manager, and your store's monthly orders keep going up. Good news, right? Not necessarily. Total orders can grow even if most new customers buy once and never return, because new people keep replacing the ones who left. To see whether customers actually stick around, product teams look at **retention**, and one of the clearest ways to show it is a **cohort retention heatmap**.

In this tutorial you'll build one with pandas and seaborn, and, just as important, learn how to read it.

## What is a cohort?

A **cohort** is a group of customers who started at the same time. Here, a cohort is everyone whose first order happened in the same month. Retention then asks a simple question: of the customers who started in a given month, what share ordered again a certain number of months later?

$$
\text{Retention}_{c,\,m} = \frac{\text{customers in cohort } c \text{ who order } m \text{ months after their first order}}{\text{customers in cohort } c}
$$

The top of the fraction counts the customers from cohort $$c$$ who came back in month $$m$$, and the bottom is everyone in that cohort. Month 0 is always 100%, since every customer orders in their first month. Every month after that shows how much of the group is still around.

## The data

We'll use real transactions from the [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail), which records every purchase from a UK-based online gift shop. I trimmed it to one row per completed order, dropping orders with no customer ID, cancelled orders, and the partial month of December 2011. That leaves **17,758 orders from 4,298 customers** between December 2010 and November 2011, with just two columns.

```python
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

url = "https://raw.githubusercontent.com/nmccaul/tutorial_blog/main/posts/data/orders.csv"
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

These steps work on any data with an ID and a date, like app logins or gym check-ins.

## Step 1: Build the cohort table

### Find each customer's cohort

First, convert each date to its month. Then find each customer's earliest month:

```python
orders["order_month"] = orders["order_date"].dt.to_period("M")
orders["cohort"] = orders.groupby("customer_id")["order_month"].transform("min")
```

We use `transform("min")` instead of `agg("min")` because `transform` returns a value for *every row*. Each order gets labeled with its customer's cohort, instead of the table collapsing to one row per customer.

### Count months since the first order

Subtracting two monthly periods gives an offset object, and `.n` pulls out the number of months:

```python
orders["months_since_first"] = (orders["order_month"] - orders["cohort"]).apply(
    lambda offset: offset.n
)
```

### Turn counts into percentages

Now count how many customers from each cohort were active in each month, then divide by the cohort's size:

```python
active = (
    orders.groupby(["cohort", "months_since_first"])["customer_id"]
    .nunique()
    .unstack()
)
cohort_size = active[0]
retention = active.div(cohort_size, axis=0)
```

A few details matter here:

- `nunique()` counts each customer **once** per month, even if they placed several orders.
- `unstack()` moves the months into columns, so each row is a cohort.
- Column `0` is the number of customers in each cohort, so dividing every row by it turns counts into shares.

Here is the top-left corner of the result:

| cohort  | 0    | 1   | 2   | 3   |
|:--------|:-----|:----|:----|:----|
| 2010-12 | 100% | 37% | 32% | 38% |
| 2011-01 | 100% | 22% | 27% | 23% |
| 2011-02 | 100% | 19% | 19% | 28% |
| 2011-03 | 100% | 15% | 25% | 20% |

That's only 16 of 144 numbers. Finding a pattern in a wall of percentages is hard, which is exactly the problem a heatmap solves.

## Step 2: Plot it with `sns.heatmap`

The simplest version is one line:

```python
sns.heatmap(retention)
```

![Default seaborn heatmap of the retention table. The month 0 column is a pale cream color, while every other cell is a similar dark purple or black. The color bar runs from about 0.15 to 1, there are no numbers in the cells, and the axis labels are the raw column names.](images/retention_heatmap_default.png)

It works, but it's hard to read. There are no numbers, darker colors mean *lower* retention, and the month 0 column (always 100%) stretches the color scale so far that every other cell lands in nearly the same dark shade. A few arguments fix all of this:

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

What each change does:

- **`annot=True, fmt=".0%"`** prints the value in each cell as a whole-number percentage, so readers don't have to guess from the color.
- **`cmap="Blues"`** uses a *sequential* palette: one color that goes from light to dark, where darker means more customers came back. Sequential palettes fit data that runs from low to high. A *diverging* palette like `"coolwarm"` is meant for data with a meaningful middle point, which retention doesn't have.
- **`vmin=0, vmax=0.5`** sets the range of the color scale. Without a cap, the 100% in month 0 sets the top of the scale and squeezes everything else together. Capping it at 50% spends the color range on the values we care about, and month 0 simply shows as the darkest shade.
- **Labels and a title** tell readers what they're looking at without reading the code.

![Seaborn heatmap of monthly customer retention for 12 cohorts, December 2010 to November 2011, using a blue color scale with the percentage printed in each cell. Month 0 is 100% for every cohort. The December 2010 cohort is darker than the rest, around 32 to 40% in most months and 50% in month 11, while later cohorts are mostly between 15 and 30%. The bottom-right triangle is empty because newer cohorts have fewer months of data.](images/retention_heatmap.png)

## Step 3: Read the heatmap

A retention heatmap can be read in four directions, and each one answers a different question:

1. **Across a row: how does one cohort change over time?** The January 2011 cohort falls to 22% in month 1 but climbs to 36% by month 10. For this store, customers who return tend to keep returning, so retention doesn't simply fade.
2. **Down a column: are newer cohorts better or worse?** Compare cohorts at the same age. In month 1, the December 2010 cohort kept 37% of its customers, while every later cohort kept between 15% and 24%.
3. **Along a diagonal: did something happen in a specific month?** Cells on the same diagonal happened in the same calendar month. The last cell in each row is November 2011, and it's the highest value in almost every row. That's holiday shopping, not a change in loyalty.
4. **The empty triangle: is data missing?** No. Newer cohorts haven't existed long enough to have a month 6 or month 10 yet.

One caution: the December 2010 cohort isn't really a group of *new* customers. The data starts on December 1, 2010, so anyone who ordered that month lands in it, including long-time customers whose actual first order was years earlier. That's part of why it looks so loyal. Before you give a cohort credit, check where your data begins.

## Try it yourself

To recap, building a retention heatmap takes five steps:

1. Label each customer with a cohort.
2. Count the months since their first order.
3. Divide unique customers per cohort and month by cohort size.
4. Plot it with `sns.heatmap`, using annotations, a sequential palette, and a capped color scale.
5. Read it across rows, down columns, and along diagonals.

**Your next step:** run this code on a dataset with an ID and a date, such as your final project data, and see what its cohorts look like. Or change `"M"` to `"W"` in `.dt.to_period("M")` to build weekly cohorts from the same orders and see how the picture changes.

Helpful resources:

- [seaborn's `heatmap` documentation](https://seaborn.pydata.org/generated/seaborn.heatmap.html)
- [pandas guide to `groupby`](https://pandas.pydata.org/docs/user_guide/groupby.html), including `transform`
- [The original UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail)

<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
