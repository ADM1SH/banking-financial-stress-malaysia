from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from pydantic import BaseModel

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class BankingStressResult(BaseModel):
    sector: str
    commercial_loans_2025_rm_mil: float
    commercial_loans_2026_rm_mil: float
    islamic_loans_2025_rm_mil: float
    islamic_loans_2026_rm_mil: float
    total_growth_pct: float
    z_score: float
    is_anomaly: bool

def analyze_banking_stress_and_anomalies(
    z_threshold: float = 1.35,
) -> Tuple[List[BankingStressResult], pd.DataFrame, Dict[str, float]]:
    df_loans = pd.read_csv(DATA_DIR / "table_4_3_4_6_bank_loans.csv")
    df_yields = pd.read_csv(DATA_DIR / "table_4_4_bond_yields.csv")

    tot_2025 = df_loans["comm_2025"] + df_loans["isl_2025"]
    tot_2026 = df_loans["comm_2026"] + df_loans["isl_2026"]
    growth_pct = ((tot_2026 - tot_2025) / tot_2025 * 100.0).values

    mean_g = float(np.mean(growth_pct))
    std_g = float(np.std(growth_pct)) if float(np.std(growth_pct)) > 0 else 1.0
    z_scores = (growth_pct - mean_g) / std_g

    results: List[BankingStressResult] = []
    for idx, row in df_loans.iterrows():
        g_val = round(float(growth_pct[idx]), 2)
        z_val = round(float(z_scores[idx]), 2)
        is_anom = bool(abs(z_val) >= z_threshold)
        results.append(
            BankingStressResult(
                sector=str(row["sector"]),
                commercial_loans_2025_rm_mil=float(row["comm_2025"]),
                commercial_loans_2026_rm_mil=float(row["comm_2026"]),
                islamic_loans_2025_rm_mil=float(row["isl_2025"]),
                islamic_loans_2026_rm_mil=float(row["isl_2026"]),
                total_growth_pct=g_val,
                z_score=z_val,
                is_anomaly=is_anom,
            )
        )
    results.sort(key=lambda x: abs(x.z_score), reverse=True)

    mgs_5y_jul = float(df_yields.loc[df_yields["instrument"] == "MGS 5-year", "jul_2026"].iloc[0])
    aaa_jul = float(df_yields.loc[df_yields["instrument"] == "Corp 5Y AAA", "jul_2026"].iloc[0])
    bbb_jul = float(df_yields.loc[df_yields["instrument"] == "Corp 5Y BBB", "jul_2026"].iloc[0])

    kpis = {
        "cet1_capital_ratio_pct": 14.6,
        "gross_impaired_loans_ratio_pct": 1.4,
        "household_debt_to_gdp_pct": 83.2,
        "median_household_dsr_pct": 32.1,
        "mgs_5y_yield_jul2026_pct": mgs_5y_jul,
        "aaa_5y_spread_bps": round((aaa_jul - mgs_5y_jul) * 100.0, 1),
        "bbb_5y_spread_bps": round((bbb_jul - mgs_5y_jul) * 100.0, 1),
    }
    return results, df_yields, kpis
