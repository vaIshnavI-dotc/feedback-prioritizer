import pandas as pd, numpy as np

def normalize_series_to_scale(s, max_score):
    # s numeric series -> 0..max_score
    if s.isnull().all():
        return pd.Series([0]*len(s), index=s.index)
    smin, smax = s.min(), s.max()
    if smax == smin:
        return pd.Series([max_score]*len(s), index=s.index) if smax>0 else pd.Series([0]*len(s), index=s.index)
    return ((s - smin) / (smax - smin)) * max_score

def urgency_value(sentiment, urgency_kws, created_at):
    # Sentiment mapping: Frustrated=25, Neutral=12, Happy=5
    base = 12
    if sentiment == "Frustrated":
        base = 25
    elif sentiment == "Happy":
        base = 5
    boost = 10 if urgency_kws and len(urgency_kws)>0 else 0
    recent = 5 if False else 0  # for demo we don't evaluate dates heavily
    return base + boost + recent

def churn_value(risk):
    if str(risk).lower().startswith("high"): return 20
    if str(risk).lower().startswith("med"): return 10
    return 5

def compute_priority_scores(df):
    f = df.copy()
    # Frequency score: based on frequency_count and unique customers in similar_feedback (approx using frequency_count)
    if 'frequency_count' not in f.columns:
        f['frequency_count'] = 1
    f['frequency_raw'] = f['frequency_count'].fillna(1).astype(float)
    freq_norm = normalize_series_to_scale(f['frequency_raw'], 20)
    f['score_frequency'] = freq_norm.round(2)
    # Revenue impact: sum of mrr per affected (we have single MRR so use it)
    if 'customer_mrr' not in f.columns:
        f['customer_mrr'] = 0
    rev_norm = normalize_series_to_scale(f['customer_mrr'].fillna(0).astype(float), 35)
    f['score_revenue_impact'] = rev_norm.round(2)
    # Urgency
    f['score_urgency'] = f.apply(lambda r: urgency_value(r.get('sentiment','Neutral'), r.get('urgency_keywords',[]), r.get('created_at', None)), axis=1)
    # normalize urgency 0-25 (they are already in 0-35 range, so scale)
    f['score_urgency'] = normalize_series_to_scale(f['score_urgency'], 25).round(2)
    # Churn
    f['score_churn'] = f['churn_risk'].apply(lambda r: churn_value(r)).astype(float)
    # Ensure churn normalized to 0-20 (already 0-20)
    # Combine
    f['priority_score'] = (f['score_frequency'] + f['score_revenue_impact'] + f['score_urgency'] + f['score_churn']).round(2)
    # score breakdown as JSON-like string
    f['score_breakdown'] = f.apply(lambda r: {"frequency": r['score_frequency'], "revenue_impact": r['score_revenue_impact'], "urgency": r['score_urgency'], "churn_risk": r['score_churn']}, axis=1)
    return f
