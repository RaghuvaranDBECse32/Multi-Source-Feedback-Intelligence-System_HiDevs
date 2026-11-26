import pandas as pd
import requests
from urllib.parse import parse_qs, urlparse

STORE_TIMEOUT = 20
USER_AGENT = "SignalFeedbackIntelligence/1.0 (public store search)"


def parse_store_url(value):
    """Return a store and app ID from a Play or App Store URL, or None."""
    value = str(value or "").strip()
    if not value:
        return None
    candidate = value if "://" in value else f"https://{value}"
    parsed = urlparse(candidate)
    host = (parsed.hostname or "").lower()
    if host.endswith("play.google.com"):
        app_id = parse_qs(parsed.query).get("id", [None])[0]
        return {"store": "Google Play", "app_id": app_id} if app_id else None
    if host.endswith("apps.apple.com") or host == "itunes.apple.com":
        segments = [segment for segment in parsed.path.split("/") if segment]
        app_id = next((segment[2:] for segment in reversed(segments) if segment.startswith("id") and segment[2:].isdigit()), None)
        return {"store": "Apple App Store", "app_id": app_id} if app_id else None
    return None


def _icon_url(app):
    return app.get("icon") or app.get("icon_url") or app.get("artworkUrl512") or app.get("artworkUrl100") or ""


def search_applications(query, country="in", limit=8, session=requests):
    """Search public Google Play and Apple catalogs. Results are never synthesized."""
    query = str(query or "").strip()
    if len(query) < 2:
        return []
    parsed = parse_store_url(query)
    if parsed:
        if parsed["store"] == "Google Play":
            try:
                from google_play_scraper import app as play_app
                item = play_app(parsed["app_id"], lang="en", country=country)
                return [_google_result(item)] if item else []
            except Exception:
                return []
        results = _apple_search(parsed["app_id"], country, limit, session, exact_id=True)
        return results

    results = []
    errors = []
    try:
        from google_play_scraper import search as play_search
        for item in play_search(query, lang="en", country=country, n_hits=limit):
            result = _google_result(item)
            if result["app_id"]:
                results.append(result)
    except Exception as exc:
        errors.append(exc)
    try:
        results.extend(_apple_search(query, country, limit, session))
    except Exception as exc:
        errors.append(exc)
    unique = {}
    for result in results:
        unique[(result["store"], result["app_id"])] = result
    if not unique and errors:
        raise RuntimeError("Could not reach either app store catalog. Check your internet connection and retry.") from errors[0]
    return list(unique.values())


def _google_result(item):
    return {"store": "Google Play", "app_id": item.get("appId", ""), "name": item.get("title", ""),
            "developer": item.get("developer", ""), "rating": item.get("score"), "icon": _icon_url(item),
            "availability": "Google Play"}


def _apple_search(term, country="in", limit=8, session=requests, exact_id=False):
    params = {"country": country, "entity": "software", "limit": limit}
    params["id" if exact_id else "term"] = term
    response = session.get("https://itunes.apple.com/search", params=params, timeout=STORE_TIMEOUT,
                           headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    results = []
    for item in response.json().get("results", []):
        app_id = str(item.get("trackId", ""))
        results.append({"store": "Apple App Store", "app_id": app_id,
                        "name": item.get("trackName", ""), "developer": item.get("sellerName", ""),
                        "rating": item.get("averageUserRating"), "icon": _icon_url(item),
                        "availability": "Apple App Store"})
    return results

def normalize(rows, source):
    df = pd.DataFrame(rows, columns=['text','date','rating'])
    df['source'] = source
    df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True).dt.tz_convert(None)
    df['text'] = df['text'].fillna('').astype(str).str.strip()
    return df.loc[df.text.ne('') & df.date.notna()].drop_duplicates(['text','date','source'])

def google_reviews(app_id, country='in', count=100):
    from google_play_scraper import reviews, Sort
    rows,_ = reviews(app_id, lang='en', country=country, sort=Sort.NEWEST, count=count)
    return normalize([(r['content'],r['at'],r['score']) for r in rows], 'Google Play')

def apple_reviews(app_id, country='in'):
    if not str(app_id).isdigit(): raise ValueError('Apple app ID must be numeric')
    response = requests.get(f'https://itunes.apple.com/{country}/rss/customerreviews/page=1/id={app_id}/sortby=mostrecent/json', timeout=STORE_TIMEOUT, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    entries=response.json().get('feed',{}).get('entry',[])
    return normalize([(r['content']['label'],r.get('updated',{}).get('label'),r['im:rating']['label']) for r in entries if 'im:rating' in r], 'Apple App Store')

def csv_reviews(file):
    df=pd.read_csv(file)
    if not {'text','date'}.issubset(df.columns): raise ValueError('CSV requires text and date columns')
    if 'rating' not in df: df['rating']=None
    return normalize(df[['text','date','rating']].itertuples(index=False,name=None), 'CSV')
