# Signal — Multi-Source Feedback Intelligence

Signal is a beginner-friendly Streamlit app for collecting public Google Play and Apple App Store reviews, analyzing survey CSV feedback, exploring VADER sentiment, prioritizing common complaints, and exporting reports. It preserves the HiDevs capstone requirements: Google reviews, Apple reviews, CSV ingestion, sentiment classification, date/source/sentiment filters, daily trends, issue prioritization, and PDF/CSV exports.

## Run locally

Python 3.11 is recommended.

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Run offline tests with:

```powershell
python -m pytest -q
```

## Four-step workflow

1. Search by application name or paste a Google Play or Apple App Store URL. Choose an exact result before collecting reviews. Quick-select buttons cover Spotify, WhatsApp, Instagram, YouTube, and Amazon.
2. Choose available review sources, country, review count, or upload a CSV (`text`, `date`, and optional `rating`). Manual store IDs remain under **Advanced settings** in the sidebar.
3. Fetch and analyze. Per-source successes and failures are reported, successful results are retained if another source fails, and previous successful results are preserved when a retry returns nothing.
4. Explore Overview, Reviews, Insights, and Reports. Filter by source, date, rating, sentiment, and review text. Export the filtered results as a PDF or analyzed CSV.

The **Use synthetic demo** button loads only the bundled `sample.csv`, labels it as synthetic, and never represents it as live store data.

## Search and collection limitations

- Google Play discovery and review collection use `google-play-scraper`, an unofficial, unaffiliated scraper. Google can change or block its endpoints, and search/review availability may vary by country and time.
- Apple application discovery uses the public iTunes Search API without an API key. Apple RSS customer-review feeds are used for review collection; availability and the number of returned pages are limited by Apple.
- Store lookups require network access. The app uses request timeouts and shows errors instead of fabricating results. No paid APIs, keys, or dummy fallback are required.
- Sentiment uses VADER and works best for English text. The displayed label strength is not calibrated confidence. Issue ranking uses keyword matches and summed negative sentiment intensity, so it is a triage aid rather than an automated diagnosis.
- Results are held in Streamlit session state; they are not persisted to a database. CSV rating values may be blank and are excluded from the average rating.

## HiDevs evaluation mapping

`sources.py` handles Google Play reviews, Apple RSS reviews, CSV normalization, URL parsing, and real application discovery. `analysis.py` provides VADER labels, review filters, daily trends, and recurring issue priority. `app.py` provides the four-step responsive UI, application selection, source status, filters, accessible chart tables, and exports. `reports.py` produces a seven-day PDF summary. `test_core.py` verifies parsing, catalog request handling, filtering, classification, trends, issue ranking, CSV serialization, and PDF generation without requiring live APIs.

Live store services and real-browser assistive technology behavior need to be checked in an environment with outbound network access and a browser. No results in this repository claim a successful live store fetch.
