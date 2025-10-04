import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import uuid, re

def normalize_text(s):
    if pd.isna(s): return ""
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def collect_and_deduplicate(df):
    # Ensure columns
    df = df.copy()
    if 'raw_text' not in df.columns:
        df['raw_text'] = df.astype(str).agg(' '.join, axis=1)
    df['raw_text'] = df['raw_text'].astype(str)
    df['norm'] = df['raw_text'].apply(normalize_text)

    # TF-IDF embed + cosine similarity
    corpus = df['norm'].tolist()
    if len(corpus) == 0:
        return df
    vect = TfidfVectorizer(ngram_range=(1,2), max_features=2000)
    X = vect.fit_transform(corpus)
    sim = cosine_similarity(X)
    n = len(df)
    groups = {}
    visited = set()
    threshold = 0.75
    for i in range(n):
        if i in visited: continue
        groups[i] = [i]
        visited.add(i)
        for j in range(i+1, n):
            if j in visited: continue
            if sim[i,j] >= threshold:
                groups[i].append(j)
                visited.add(j)
    # Merge groups
    rows = []
    for leader, idxs in groups.items():
        texts = df.iloc[idxs]['raw_text'].tolist()
        sources = df.iloc[idxs].get('source', pd.Series(['unknown']*len(idxs))).tolist()
        emails = df.iloc[idxs].get('customer_email', pd.Series([None]*len(idxs))).tolist()
        createds = df.iloc[idxs].get('created_at', pd.Series([None]*len(idxs))).tolist()
        merged = {
            "id": str(uuid.uuid4()),
            "raw_text": texts[0],
            "raw_texts_merged": texts,
            "source": list(set(sources)),
            "customer_email": next((e for e in emails if pd.notna(e)), None),
            "created_at": createds[0] if createds else None,
            "frequency_count": len(idxs),
        }
        rows.append(merged)
    out = pd.DataFrame(rows)
    return out
