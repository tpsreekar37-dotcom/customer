import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Show model results
with open('models/model_results.json') as f:
    results = json.load(f)
print('=== MODEL COMPARISON ===')
for r in results:
    print(f"  {r['model']:<22} AUC={r['roc_auc']:.4f}  F1={r['f1']:.4f}  Recall={r['recall']:.4f}  Precision={r['precision']:.4f}")

# Show feature importance top 10
import pandas as pd
fi = pd.read_csv('models/feature_importance.csv')
print()
print('=== TOP 10 CHURN PREDICTORS ===')
for i, row in fi.head(10).iterrows():
    bar = '#' * int(row['Importance'] * 200)
    print(f"  {i+1:2}. {row['Feature']:<22} {bar} ({row['Importance']:.4f})")

# Show SQL summary
try:
    from src.sql_integration import run_analytics, get_latest_run_id
    run_id = get_latest_run_id()
    if run_id:
        analytics = run_analytics(run_id=run_id)
        print()
        print(f'=== BUSINESS SUMMARY (Run: {run_id}) ===')
        summary = analytics.get('churn_summary')
        if summary is not None and not summary.empty:
            s_row = summary.iloc[0]
            print(f"  Total Customers  : {int(s_row.get('total_customers', 0)):,}")
            print(f"  Predicted Churned: {int(s_row.get('total_churned', 0)):,}")
            print(f"  Churn Rate       : {float(s_row.get('churn_rate_pct', 0)):.2f}%")
        rev = analytics.get('revenue_at_risk')
        if rev is not None and not rev.empty:
            r_row = rev.iloc[0]
            print(f"  Revenue at Risk  : ${float(r_row.get('monthly_revenue_at_risk', 0)):,.0f}/month (MRR)")
            print(f"  Annual Exposure  : ${float(r_row.get('annual_revenue_at_risk', 0)):,.0f}/year (ARR)")

        print()
        print('=== CHURN BY CONTRACT TYPE ===')
        by_contract = analytics.get('churn_by_contract')
        if by_contract is not None and not by_contract.empty:
            for _, row in by_contract.iterrows():
                c_name = row.get('Contract', 'Unknown')
                c_rate = row.get('churn_rate_pct', 0)
                c_churned = int(row.get('churned', 0))
                c_total = int(row.get('total_customers', 0))
                print(f"  {str(c_name):<18} {c_rate:.1f}% churn  ({c_churned}/{c_total} customers)")
except Exception as e:
    print(f"SQL summary note: {e}")
