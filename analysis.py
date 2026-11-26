import re
import pandas as pd

ISSUES={'Performance':r'\b(slow|lag|freeze|freezes|loading|crash|crashes)\b','Login':r'\b(login|password|sign in|otp)\b','Payments':r'\b(payment|refund|charged|billing|subscription)\b','Connectivity':r'\b(network|offline|connection|internet)\b','Usability':r'\b(confusing|interface|navigation|hard to use)\b','Bugs':r'\b(bug|error|broken|not working)\b'}

def classify(df, scorer=None):
    if scorer is None:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        scorer=SentimentIntensityAnalyzer().polarity_scores
    out=df.copy()
    scores=[scorer(t) for t in out.text]
    out['score']=[s['compound'] for s in scores]
    out['sentiment']=['Positive' if s>=.05 else 'Negative' if s<=-.05 else 'Neutral' for s in out.score]
    out['confidence']=[s[{'Positive':'pos','Negative':'neg','Neutral':'neu'}[label]] for s,label in zip(scores,out.sentiment)]
    return out

def trends(df):
    return df.assign(day=df.date.dt.floor('D')).groupby('day').score.agg(['mean','count']).reset_index()

def filter_reviews(df, sources=None, sentiments=None, date_range=None, rating_range=None, query=""):
    """Apply dashboard filters consistently; missing ratings remain visible unless a rating range is set."""
    out = df.copy()
    if sources is not None:
        out = out[out.source.isin(sources)]
    if sentiments is not None:
        out = out[out.sentiment.isin(sentiments)]
    if date_range and len(date_range) == 2:
        start, end = date_range
        dates = pd.to_datetime(out.date, errors="coerce").dt.date
        out = out[dates.between(start, end)]
    if rating_range is not None and out.rating.notna().any():
        low, high = rating_range
        ratings = pd.to_numeric(out.rating, errors="coerce")
        out = out[ratings.isna() | ratings.between(low, high)]
    if query and str(query).strip():
        out = out[out.text.astype(str).str.contains(str(query).strip(), case=False, regex=False, na=False)]
    return out

def issues(df):
    neg=df[df.sentiment.eq('Negative')]
    rows=[]
    for name,pattern in ISSUES.items():
        subset=neg[neg.text.str.contains(pattern,case=False,regex=True)]
        if len(subset): rows.append((name,len(subset),round(float(-subset.score.sum()),2)))
    return pd.DataFrame(rows,columns=['issue','frequency','priority']).sort_values('priority',ascending=False)
