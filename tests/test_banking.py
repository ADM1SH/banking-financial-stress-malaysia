from src.banking_model import analyze_banking_stress_and_anomalies

def test_banking():
    stress_list, df_yields, kpis = analyze_banking_stress_and_anomalies(1.35)
    assert len(stress_list) == 13
    assert len(df_yields) == 8
    assert kpis["gross_impaired_loans_ratio_pct"] == 1.4
