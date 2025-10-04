import pandas as pd
from dateutil import parser
def enrich_with_crm(feedback_df, crm_df):
    f = feedback_df.copy()
    crm = crm_df.copy()
    crm['customer_email'] = crm['customer_email'].astype(str).str.lower()
    f['customer_email'] = f['customer_email'].astype(str).str.lower()
    # naive join by email
    merged = f.merge(crm, how='left', left_on='customer_email', right_on='customer_email', suffixes=('','_crm'))
    # fill defaults
    merged['customer_mrr'] = merged.get('mrr', 0).fillna(0)
    merged['customer_tier'] = merged.get('tier', 'SMB').fillna('SMB')
    # churn risk heuristic
    def churn_risk(row):
        risk = "Low"
        try:
            if row.get('usage_drop', False) or (row.get('renewal_date') and parser.parse(str(row.get('renewal_date'))) < parser.parse("2026-01-01")):
                risk = "High"
        except Exception:
            risk = "Low"
        return risk
    merged['churn_risk'] = merged.apply(churn_risk, axis=1)
    # keep columns expected downstream
    cols = list(merged.columns)
    return merged
