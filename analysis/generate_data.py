"""Generate a realistic synthetic sales dataset for a fictional Tunisian SME.

Business: 'Dar El Baraka' - a Tunis-based distributor of Tunisian food products
selling through retail shops, wholesale partners and an online store.

Period: 2024-04-01 to 2025-09-30 (18 months), ~one row per order line.
Built-in storylines for the analysis to discover:
  1. Overall revenue grows, but the Wholesale channel has been declining for
     the last ~4 months (a key client churned).
  2. Dates (Deglet Nour) are strongly seasonal - Q4 spike (autumn harvest).
  3. Olive oil carries the highest discounts, eroding margin despite high revenue.
  4. Online is small but the fastest-growing channel with the best margin.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

PRODUCTS = [
    # (product, category, unit_price TND, unit_cost TND)
    ("Huile d'Olive Extra Vierge 1L", "Olive Oil", 28.5, 19.0),
    ("Huile d'Olive Extra Vierge 5L", "Olive Oil", 132.0, 92.0),
    ("Dattes Deglet Nour 1kg", "Dates", 14.0, 8.5),
    ("Dattes Deglet Nour 5kg", "Dates", 62.0, 39.0),
    ("Harissa Traditionnelle 200g", "Condiments", 6.5, 3.2),
    ("Harissa 1kg (pro)", "Condiments", 24.0, 12.5),
    ("Couscous Fin 1kg", "Grains", 5.8, 3.4),
    ("Couscous Complet 1kg", "Grains", 7.2, 4.1),
    ("Bsissa Traditionnelle 500g", "Grains", 9.5, 5.0),
    ("Miel de Thym 250g", "Honey", 32.0, 20.0),
]

REGIONS = ["Tunis", "Sfax", "Sousse", "Gabes", "Bizerte", "Monastir"]
REGION_W = [0.30, 0.20, 0.16, 0.12, 0.12, 0.10]

CHANNELS = ["Retail", "Wholesale", "Online"]

start = pd.Timestamp("2024-04-01")
end = pd.Timestamp("2025-09-30")
dates = pd.date_range(start, end, freq="D")

rows = []
order_id = 1000
for day in dates:
    m = day.month
    # base daily order volume grows slowly over time (business growth)
    growth = 1 + (day - start).days / 540 * 0.55
    # Ramadan-ish / autumn seasonality: more orders Oct-Dec and Mar-Apr
    seasonal = 1.0 + (0.45 if m in (10, 11, 12) else 0) + (0.20 if m in (3, 4) else 0)
    n_orders = rng.poisson(3.2 * growth * seasonal)
    for _ in range(n_orders):
        order_id += 1
        prod = PRODUCTS[rng.integers(len(PRODUCTS))]
        product, category, price, cost = prod
        region = rng.choice(REGIONS, p=REGION_W)

        # channel mix shifts over time: wholesale declines from 2025-06
        if day >= pd.Timestamp("2025-06-01"):
            ch_p = [0.52, 0.22, 0.26]
        elif day >= pd.Timestamp("2024-10-01"):
            ch_p = [0.50, 0.32, 0.18]
        else:
            ch_p = [0.48, 0.38, 0.14]
        channel = rng.choice(CHANNELS, p=ch_p)

        qty = int(rng.choice([1, 2, 3, 4, 6, 10, 12, 20],
                             p=[0.28, 0.22, 0.15, 0.10, 0.08, 0.07, 0.05, 0.05]))
        if channel == "Wholesale":
            qty = int(qty * rng.choice([3, 4, 5]))

        # dates spike in Q4 (harvest season)
        if category == "Dates" and m in (10, 11, 12):
            qty = int(qty * 2.2)

        # olive oil gets the deepest discounts (margin story)
        if category == "Olive Oil":
            discount = float(rng.choice([0, 5, 10, 15, 20], p=[0.25, 0.25, 0.25, 0.15, 0.10]))
        else:
            discount = float(rng.choice([0, 0, 5, 10], p=[0.45, 0.25, 0.20, 0.10]))

        revenue = round(qty * price * (1 - discount / 100), 2)
        profit = round(revenue - qty * cost, 2)
        rows.append([order_id, day.date().isoformat(), product, category,
                     region, channel, qty, price, discount, revenue, profit])

df = pd.DataFrame(rows, columns=[
    "order_id", "date", "product", "category", "region", "channel",
    "quantity", "unit_price_tnd", "discount_pct", "revenue_tnd", "profit_tnd",
])

# sprinkle a few messy rows like real data (to be cleaned in analysis)
mess = df.sample(8, random_state=7).copy()
mess["region"] = mess["region"].str.lower()          # inconsistent casing
df = pd.concat([df, mess], ignore_index=True).sample(frac=1, random_state=11).reset_index(drop=True)

out = "/home/hatch/workspace/portfolio/01-sales-dashboard-tunisian-sme/data/sales_data.csv"
df.to_csv(out, index=False)
print(f"rows={len(df)} cols={list(df.columns)}")
print(df.head(3).to_string())
print("date range:", df["date"].min(), "->", df["date"].max())
