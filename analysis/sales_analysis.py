"""Sales analysis for Dar El Baraka (fictional Tunisian SME).

Steps: load -> clean -> KPIs -> charts -> findings (printed).
Charts are saved to ../visuals/ and embedded in the Excel dashboard.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "sales_data.csv"
VIS = BASE / "visuals"
VIS.mkdir(exist_ok=True)

plt.rcParams.update({"figure.dpi": 150, "font.size": 10})

# ---------- load & clean ----------
df = pd.read_csv(DATA, parse_dates=["date"])
print(f"raw rows: {len(df)}")

df["region"] = df["region"].str.strip().str.title()          # fix casing mess
df = df.drop_duplicates(subset=["order_id"], keep="first")  # drop dup orders
df = df[df["quantity"] > 0].copy()
df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
print(f"clean rows: {len(df)}")

# ---------- KPIs ----------
total_rev = df["revenue_tnd"].sum()
total_profit = df["profit_tnd"].sum()
margin = total_profit / total_rev * 100
n_orders = df["order_id"].nunique()
aov = total_rev / n_orders

monthly = df.groupby("month").agg(revenue=("revenue_tnd", "sum"),
                                  profit=("profit_tnd", "sum"),
                                  orders=("order_id", "nunique")).reset_index()
monthly["mom_growth"] = monthly["revenue"].pct_change() * 100

first6 = monthly.head(6)["revenue"].mean()
last6 = monthly.tail(6)["revenue"].mean()

by_channel = df.groupby("channel").agg(revenue=("revenue_tnd", "sum"),
                                       profit=("profit_tnd", "sum"),
                                       orders=("order_id", "nunique"))
by_channel["margin_pct"] = by_channel["profit"] / by_channel["revenue"] * 100
by_channel["aov"] = by_channel["revenue"] / by_channel["orders"]

by_cat = df.groupby("category").agg(revenue=("revenue_tnd", "sum"),
                                    profit=("profit_tnd", "sum"),
                                    avg_discount=("discount_pct", "mean"))
by_cat["margin_pct"] = by_cat["profit"] / by_cat["revenue"] * 100

by_region = df.groupby("region")["revenue_tnd"].sum().sort_values(ascending=False)
by_product = df.groupby("product")["revenue_tnd"].sum().sort_values(ascending=False)

# wholesale trend: first 9 months vs last 4 months (decline story)
wh = df[df["channel"] == "Wholesale"].groupby("month")["revenue_tnd"].sum()
wh_early, wh_late = wh.head(9).mean(), wh.tail(4).mean()
wh_drop = (wh_late - wh_early) / wh_early * 100

print(f"\nTotal revenue: {total_rev:,.0f} TND | Profit: {total_profit:,.0f} TND | Margin: {margin:.1f}%")
print(f"Orders: {n_orders} | AOV: {aov:.1f} TND")
print(f"Avg monthly revenue first 6m: {first6:,.0f} -> last 6m: {last6:,.0f} "
      f"({(last6-first6)/first6*100:+.1f}%)")
print(f"Wholesale avg monthly: early {wh_early:,.0f} -> recent {wh_late:,.0f} ({wh_drop:+.1f}%)")
print("\nChannel mix:\n", by_channel.round(1).to_string())
print("\nCategory margin:\n", by_cat.round(1).to_string())
print("\nTop 3 products:\n", by_product.head(3).to_string())

# ---------- charts ----------
# 1. monthly revenue trend with channel split
ch_month = df.groupby(["month", "channel"])["revenue_tnd"].sum().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(10, 4.5))
ch_month.plot(kind="bar", stacked=True, ax=ax, width=0.85,
              color=["#2E86AB", "#E67E22", "#27AE60"])
ax.set_title("Monthly Revenue by Channel (TND) - Dar El Baraka")
ax.set_xlabel(""); ax.set_ylabel("Revenue (TND)")
ax.legend(title="Channel")
ax.set_xticklabels([pd.Timestamp(m).strftime("%b %Y") for m in ch_month.index], rotation=45, ha="right")
plt.tight_layout(); plt.savefig(VIS / "monthly_revenue_by_channel.png"); plt.close()

# 2. top products
fig, ax = plt.subplots(figsize=(9, 4.5))
by_product.head(8).sort_values().plot(kind="barh", ax=ax, color="#2E86AB")
ax.set_title("Top 8 Products by Revenue (TND)")
ax.set_xlabel("Revenue (TND)")
plt.tight_layout(); plt.savefig(VIS / "top_products.png"); plt.close()

# 3. category margin vs avg discount
fig, ax1 = plt.subplots(figsize=(9, 4.5))
x = np.arange(len(by_cat))
ax1.bar(x, by_cat["margin_pct"], color="#27AE60", label="Margin %")
ax1.set_xticks(x); ax1.set_xticklabels(by_cat.index, rotation=20, ha="right")
ax1.set_ylabel("Margin %"); ax1.set_title("Margin % vs Avg Discount % by Category")
ax2 = ax1.twinx()
ax2.plot(x, by_cat["avg_discount"], color="#C0392B", marker="o", label="Avg discount %")
ax2.set_ylabel("Avg discount %")
fig.tight_layout(); plt.savefig(VIS / "category_margin_discount.png"); plt.close()

# 4. region share
fig, ax = plt.subplots(figsize=(7, 4.5))
by_region.plot(kind="pie", ax=ax, autopct="%1.0f%%", startangle=90,
               colors=plt.cm.Blues(np.linspace(0.35, 0.85, len(by_region))))
ax.set_title("Revenue Share by Region"); ax.set_ylabel("")
plt.tight_layout(); plt.savefig(VIS / "revenue_by_region.png"); plt.close()

# save cleaned data + monthly table for the Excel dashboard
df.to_csv(BASE / "data" / "sales_data_clean.csv", index=False)
monthly.to_csv(BASE / "data" / "monthly_summary.csv", index=False)
print("\ncharts + cleaned data saved.")
