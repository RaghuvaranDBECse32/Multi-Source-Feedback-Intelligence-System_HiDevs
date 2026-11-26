import pandas as pd
import pytest

from analysis import classify, filter_reviews, issues, trends
from reports import weekly_pdf
from sources import _apple_search, csv_reviews, normalize, parse_store_url


def scorer(text):
    bad = any(x in text.lower() for x in ["error", "slow", "failed", "broken"])
    return {"compound": -.8 if bad else .7, "neg": .8 if bad else 0, "pos": 0 if bad else .7, "neu": .2}


def test_pipeline_and_exports():
    frame = csv_reviews("sample.csv")
    result = classify(frame, scorer)
    assert len(result) == 6
    assert len(trends(result)) == 6
    assert "Login" in issues(result).issue.values
    pdf = weekly_pdf(result)
    assert pdf.startswith(b"%PDF")
    assert pd.to_numeric(result.rating, errors="coerce").mean() == pytest.approx(8 / 3)
    assert result.to_csv(index=False).encode("utf-8-sig").startswith(b"\xef\xbb\xbf")


@pytest.mark.parametrize("url,expected", [
    ("https://play.google.com/store/apps/details?id=com.spotify.music", {"store":"Google Play","app_id":"com.spotify.music"}),
    ("https://apps.apple.com/in/app/spotify-music-and-podcasts/id324684580", {"store":"Apple App Store","app_id":"324684580"}),
    ("https://itunes.apple.com/us/app/thing/id123456", {"store":"Apple App Store","app_id":"123456"}),
])
def test_store_url_parsing(url, expected):
    assert parse_store_url(url) == expected


def test_url_parser_rejects_unknown_host_and_incomplete_store_link():
    assert parse_store_url("https://example.com/?id=foo") is None
    assert parse_store_url("https://play.google.com/store/apps/details") is None


def test_apple_search_uses_public_lookup_and_normalizes_result():
    class Response:
        def raise_for_status(self): pass
        def json(self):
            return {"results":[{"trackId":12,"trackName":"Example","sellerName":"Maker","averageUserRating":4.5,"artworkUrl100":"https://img.invalid/app.png"}]}
    class Session:
        def get(self, url, params, timeout, headers):
            assert url == "https://itunes.apple.com/search"
            assert params["term"] == "Example"
            assert params["country"] == "in"
            assert timeout > 0
            return Response()
    result = _apple_search("Example", session=Session())
    assert result[0]["app_id"] == "12"
    assert result[0]["name"] == "Example"
    assert result[0]["rating"] == 4.5
    assert result[0]["icon"].endswith("app.png")


def test_filter_controls_source_date_rating_sentiment_and_text():
    df = classify(csv_reviews("sample.csv"), scorer)
    result = filter_reviews(df, sources=["CSV"], sentiments=["Negative"],
                            date_range=(pd.Timestamp("2026-11-21").date(), pd.Timestamp("2026-11-26").date()),
                            rating_range=(1, 2), query="login")
    assert len(result) == 1
    assert result.iloc[0].rating == 1
    assert result.iloc[0].sentiment == "Negative"


def test_rating_filter_keeps_missing_rating_rows():
    df = pd.DataFrame([{"text":"Fine","date":"2026-11-01","rating":None,"source":"CSV","sentiment":"Neutral","score":0,"confidence":1}])
    assert len(filter_reviews(df, rating_range=(1, 2))) == 1


def test_rating_filter_does_not_hide_csv_without_any_ratings():
    df = pd.DataFrame([{"text":"Good","date":"2026-11-01","rating":None,"source":"CSV","sentiment":"Positive","score":.5,"confidence":.8}])
    assert len(filter_reviews(df, rating_range=(4, 5))) == 1


def test_normalize_discards_blank_and_invalid_dates():
    result = normalize([("ok", "2026-01-01", 5), ("", "2026-01-01", 4), ("bad date", "no-date", 2)], "test")
    assert len(result) == 1


def test_pdf_handles_empty_filtered_result():
    assert weekly_pdf(pd.DataFrame()).startswith(b"%PDF")
