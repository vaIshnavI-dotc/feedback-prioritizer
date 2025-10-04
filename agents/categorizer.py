import pandas as pd, re
def detect_sentiment(text):
    # tiny lexicon-based sentiment
    pos = set(["good","great","love","awesome","fast","easy","works","nice"])
    neg = set(["slow","frustrat","hate","bug","error","fail","can't","can't","cannot","broken","problem","issue","frustrating","terrible","bad"])
    t = text.lower()
    score = 0
    for w in pos:
        if w in t: score += 1
    for w in neg:
        if w in t: score -= 1
    if score <= -1: return "Frustrated"
    if score == 0: return "Neutral"
    return "Happy"

def keyword_classify(text):
    t = text.lower()
    if any(k in t for k in ["error","bug","crash","exception"]):
        return "Bug", "Backend"
    if any(k in t for k in ["slow","lag","delay","performance","takes forever","loading"]):
        return "Performance", "Auth/UI"
    if any(k in t for k in ["login","signup","password","auth"]):
        return "UX Issue", "Auth"
    if any(k in t for k in ["invoice","billing","charge","payment","stripe"]):
        return "Billing", "Billing"
    if any(k in t for k in ["api","endpoint","webhook"]):
        return "Integration", "API"
    return "Feature Request", "Dashboard"

def extract_urgency_keywords(text):
    kws = []
    for k in ["blocker","urgent","can't use","can't","deal-breaker","blocking","critical","asap","immediately","error"]:
        if k in text.lower():
            kws.append(k)
    return kws

def categorize_feedback(df):
    f = df.copy()
    f['sentiment'] = f['raw_text'].apply(detect_sentiment)
    types = []
    areas = []
    urgks = []
    for t in f['raw_text']:
        typ, area = keyword_classify(t)
        types.append(typ)
        areas.append(area)
        urgks.append(extract_urgency_keywords(t))
    f['category_type'] = types
    f['category_area'] = areas
    f['urgency_keywords'] = urgks
    return f
