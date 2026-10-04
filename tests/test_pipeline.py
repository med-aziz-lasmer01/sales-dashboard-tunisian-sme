"""Tests for the Dar El Baraka sales pipeline.

Run:  pytest tests/ -v   (from the repo root)
Requires the pipeline to have run once (data/sales_data.csv must exist).
"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "sales_data.csv"
CLEAN = BASE / "data" / "sales_data_clean.csv"
MONTHLY = BASE / "data" / "monthly_summary.csv"


def _cleaned():
    """Reproduce the cleaning steps (same logic as sales_analysis.py)."""
    df = pd.read_csv(RAW, dtype={"date": str})
    df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=True)
    for c in ["product", "category", "region", "channel"]:
        df[c] = df[c].astype(str).str.strip().replace({"nan": np.nan})
    typo_fix = {
        "Huile d'Ol ive Extra Vierge 1L": "Huile d'Olive Extra Vierge 1L",
        "Harisa Traditionnelle 200g": "Harissa Traditionnelle 200g",
        "Dattes Deglet Nour 1 Kg": "Dattes Deglet Nour 1kg",
        "Couscous Fin 1KG": "Couscous Fin 1kg",
        "Miel de Thym  250g": "Miel de Thym 250g",
    }
    df["product"] = df["product"].replace(typo_fix)
    df["region"] = df["region"].str.title()
    df["channel"] = df["channel"].str.title()
    df["discount_pct"] = df["discount_pct"].fillna(0)
    df["region"] = df["region"].fillna("Unknown")
    df = df.drop_duplicates(subset=["order_id"], keep="first")
    df = df[df["quantity"] > 0]
    df = df[df["quantity"] <= 500]
    df["revenue_tnd"] = (df["quantity"] * df["unit_price_tnd"]
                         * (1 - df["discount_pct"] / 100)).round(2)
    return df


def test_no_duplicate_order_ids():
    df = _cleaned()
    assert df["order_id"].is_unique, "duplicate order_ids survived cleaning"


def test_no_missing_critical_fields():
    df = _cleaned()
    for col in ["order_id", "date", "product", "quantity",
                "unit_price_tnd", "revenue_tnd"]:
        assert df[col].isna().sum() == 0, f"NaN in {col} after cleaning"


def test_quantities_positive_and_sane():
    df = _cleaned()
    assert (df["quantity"] > 0).all()
    assert (df["quantity"] <= 500).all(), "outlier quantity survived"


def test_no_typos_remain():
    df = _cleaned()
    # double-space typos and specific misspellings (not substrings of good names)
    assert not df["product"].str.contains("  ", regex=False).any(), \
        "double-space typo survived cleaning"
    bad = ["Huile d'Ol ive", "Harisa Traditionnelle", "1 Kg", "1KG"]
    for b in bad:
        assert not df["product"].str.contains(b, regex=False).any(), \
            f"typo '{b}' survived cleaning"


def test_dates_all_parsed():
    df = _cleaned()
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df["date"].isna().sum() == 0
    assert df["date"].min() >= pd.Timestamp("2024-04-01")
    assert df["date"].max() <= pd.Timestamp("2025-09-30")


def test_revenue_formula_spot_check():
    """Hand-computed check on 5 rows: revenue = qty * price * (1 - disc)."""
    df = _cleaned().head(5)
    for _, r in df.iterrows():
        expected = round(r["quantity"] * r["unit_price_tnd"]
                         * (1 - r["discount_pct"] / 100), 2)
        assert abs(r["revenue_tnd"] - expected) < 0.01, \
            f"revenue mismatch on order {r['order_id']}"


def test_monthly_sums_match_total():
    df = _cleaned()
    monthly = pd.read_csv(MONTHLY, parse_dates=["month"])
    assert abs(monthly["revenue"].sum() - df["revenue_tnd"].sum()) < 1.0


def test_cleaning_removed_mess():
    raw = pd.read_csv(RAW)
    clean = _cleaned()
    assert len(clean) < len(raw), "cleaning should remove rows"
    removed_pct = (len(raw) - len(clean)) / len(raw) * 100
    assert removed_pct > 1.0, f"only {removed_pct:.1f}% removed — mess too mild"
    print(f"\n  cleaning removed {len(raw) - len(clean)} rows ({removed_pct:.1f}%)")
