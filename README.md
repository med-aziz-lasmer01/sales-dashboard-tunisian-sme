# Sales Dashboard — Dar El Baraka (Tunisian SME)

A complete, client-style data analysis case study: from messy raw orders to
an executive dashboard with business recommendations.

**Business:** *Dar El Baraka*, a fictional Tunis-based distributor of Tunisian
food products (olive oil, Deglet Nour dates, harissa, grains, honey) selling
through retail shops, wholesale partners and an online store.

## The Problem

The owner sees revenue growing but profit feels flat. Three questions:
1. Which channels and products actually make money?
2. Why did wholesale revenue fall off a cliff in 2025?
3. Where should they invest next — retail, wholesale recovery, or online?

## The Data

- `data/sales_data.csv` — 2,468 raw order lines (Apr 2024 → Sep 2025), with
  realistic messiness: duplicate order IDs, inconsistent region casing
- `data/sales_data_clean.csv` — cleaned dataset (2,460 rows)
- `data/monthly_summary.csv` — month-level aggregates

## The Process

1. **Clean** (`analysis/sales_analysis.py`): fixed region casing, removed
   duplicate orders, validated quantities
2. **Analyze**: KPIs, month-over-month trends, channel / category / region splits,
   margin vs. discount analysis
3. **Visualize**: 4 charts in `visuals/`
4. **Deliver**: `dashboard/Sales_Dashboard.xlsx` — Cover, raw Data, KPI Dashboard
   with embedded charts, and Monthly breakdown

Run it yourself:
```bash
pip install -r requirements.txt
python analysis/generate_data.py   # regenerate the dataset
python analysis/sales_analysis.py  # cleaning + KPIs + charts
python analysis/build_excel.py     # build the Excel dashboard
```

## The Results

| KPI | Value |
|---|---|
| Total revenue (18 months) | **613,848 TND** |
| Total profit | **201,152 TND** |
| Profit margin | **32.8%** |
| Orders | 2,460 · AOV **249.5 TND** |
| Revenue trend | **+9.9%** (first 6 months avg → last 6 months avg) |

**Key findings:**
- 🔴 **Wholesale collapsed**: from ~24,200 TND/month to ~11,900 TND/month
  (**-51%**) in the last 4 months — the single biggest risk to the business.
- 🫒 **Olive oil is a margin trap**: 42% of revenue but only **24.3% margin**,
  dragged down by the deepest discounts (avg **8.2%** vs ~2% elsewhere).
- 🟢 **Online is the growth engine**: smallest channel today, but the only one
  gaining share every quarter, with a healthy 32% margin.
- 📅 **Dates are seasonal**: Q4 (harvest) drives a massive spike — stock-outs
  in autumn mean leaving money on the table.

## Recommendations

1. **Recover wholesale immediately** — call the churned key accounts; ~12k
   TND/month is leaking.
2. **Cap olive-oil discounts at 5%** and replace deeper cuts with bundles
   (oil + harissa) to protect margin.
3. **Invest in online**: it converts growth into profit better than any channel.
4. **Plan Q4 inventory for dates** in August, not October.

## Tools

Python (pandas, matplotlib, openpyxl) · Excel · CSV
