import pandas as pd
import plotly.express as px
import streamlit as st

from analysis import classify, filter_reviews, issues, trends
from reports import weekly_pdf
from sources import apple_reviews, csv_reviews, google_reviews, parse_store_url, search_applications

st.set_page_config(page_title="Signal — Feedback Intelligence", page_icon="◉", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--bg:#0d0f12;--surface:#17191e;--raised:#202329;--line:#41444d;--text:#f5f5f7;--muted:#c0c1c8;--blue:#8ab8ff}
.stApp{background:radial-gradient(ellipse at 8% 0%,rgba(66,133,244,.11),transparent 32%),radial-gradient(ellipse at 95% 35%,rgba(8,102,255,.06),transparent 28%),var(--bg);color:var(--text);font-family:'DM Sans',sans-serif}
.stApp:before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.08;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.13'/%3E%3C/svg%3E")}
.block-container{max-width:1440px;padding:1rem clamp(1rem,3vw,2.5rem) 3rem} h1,h2,h3{font-family:'Manrope',sans-serif!important;letter-spacing:-.04em!important;color:var(--text)!important}
.topbar{display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding:4px 0 14px;border-bottom:1px solid #343740;margin-bottom:18px}.brand{font:800 20px Manrope,sans-serif;letter-spacing:-.05em}.brand-mark{color:#8ab8ff;margin-right:9px}.eyebrow{color:#a8caff;text-transform:uppercase;letter-spacing:.13em;font-size:10px;font-weight:700}.hero{margin:0 0 17px}.hero h1{font-size:clamp(30px,4vw,42px);line-height:1.08;margin:6px 0}.hero p{color:#c0c1c8;font-size:14px;margin:0;max-width:680px;line-height:1.6}.step-label{font:700 15px Manrope,sans-serif;margin:10px 0 8px;color:#f5f5f7}.section-title{font:700 18px Manrope,sans-serif;margin:22px 0 4px}.section-sub{color:#c0c1c8;font-size:13px;margin-bottom:12px}
div[data-testid="stMetric"]{padding:15px;border-radius:15px;background:linear-gradient(145deg,#202329,#191b20);border:1px solid #41444d;min-height:108px}div[data-testid="stMetricLabel"]{color:#c0c1c8!important;font-size:13px!important}div[data-testid="stMetricValue"]{color:#f5f5f7!important;font:700 25px Manrope,sans-serif!important}
div[data-testid="stVerticalBlockBorderWrapper"]{background:linear-gradient(145deg,#1b1d22,#17191e);border-color:#41444d;border-radius:16px}
.stButton>button,.stDownloadButton>button{min-height:44px;border-radius:12px;border:1px solid #50545e;background:#24272e;color:#f5f5f7;padding:9px 15px;font-weight:600}.stButton>button:hover,.stDownloadButton>button:hover{border-color:#8ab8ff;color:white}.stButton>button:focus-visible,.stDownloadButton>button:focus-visible, input:focus-visible{outline:3px solid #a8caff!important;outline-offset:2px!important}
div[data-baseweb="select"]>div,div[data-baseweb="input"]>div{background:#17191e;border-color:#50545e;border-radius:11px}label, [data-testid="stWidgetLabel"]{color:#f0f0f3!important;font-weight:600!important}div[data-testid="stDataFrame"]{border:1px solid #41444d;border-radius:14px;overflow:hidden}
.result{display:flex;align-items:center;gap:12px;padding:12px;border:1px solid #41444d;border-radius:13px;margin:8px 0;background:#191b20}.result img{width:52px;height:52px;border-radius:12px;object-fit:cover}.muted{color:#c0c1c8;font-size:12px}
@media(max-width:760px){.block-container{padding:12px 12px 36px}.hero h1{font-size:32px}.result img{width:44px;height:44px}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{scroll-behavior:auto!important;transition:none!important;animation:none!important}}
</style>""", unsafe_allow_html=True)

if "light_theme" not in st.session_state:
    st.session_state.light_theme = False
with st.sidebar:
    st.markdown("### ◉ Signal")
    st.caption("Feedback intelligence")
    st.session_state.light_theme = st.toggle("Light appearance", value=st.session_state.light_theme)
    st.markdown("---")
    st.markdown("#### Advanced settings")
    manual_google = st.text_input("Google Play package ID", "", help="Use this if search cannot find the application.")
    manual_apple = st.text_input("Apple App Store numeric ID", "", help="Use this if search cannot find the application.")

if st.session_state.light_theme:
    st.markdown("<style>:root{--bg:#f4f6fa;--text:#17191e}.stApp{background:#f4f6fa;color:#17191e}h1,h2,h3,.section-title,.step-label{color:#17191e!important}.hero p,.section-sub,.muted{color:#505662}div[data-testid='stMetric']{background:#fff;border-color:#dfe3eb}div[data-testid='stMetricLabel']{color:#505662!important}div[data-testid='stMetricValue']{color:#17191e!important}.stButton>button,.stDownloadButton>button{background:#fff;color:#17191e;border-color:#b7bdc9}div[data-baseweb='select']>div,div[data-baseweb='input']>div{background:#fff;border-color:#aeb5c1}label,[data-testid='stWidgetLabel']{color:#17191e!important}div[data-testid='stVerticalBlockBorderWrapper']{background:#fff;border-color:#d2d7e0}.result{background:#fff;border-color:#d2d7e0}.topbar{border-color:#d2d7e0}</style>", unsafe_allow_html=True)

st.markdown('<div class="topbar"><div class="brand"><span class="brand-mark">◉</span>Signal</div><span class="muted">Feedback intelligence for every app</span></div>', unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="eyebrow">VOICE OF CUSTOMER · REVIEW ANALYTICS</div><h1>Every review, made meaningful.</h1><p>Find your app, bring feedback together, and see what customers want you to improve.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="step-label">Step 1 of 4 · Search and select an application</div>', unsafe_allow_html=True)
quick = st.columns([1, 1, 1, 1, 1, 1.5], gap="small")
for col, name in zip(quick[:5], ["Spotify", "WhatsApp", "Instagram", "YouTube", "Amazon"]):
    with col:
        if st.button(name, key=f"quick_{name}", use_container_width=True):
            st.session_state.app_query = name
with quick[5]:
    if st.button("Use synthetic demo", help="Loads the bundled sample.csv, clearly labelled as synthetic data.", use_container_width=True):
        demo_df = csv_reviews("sample.csv").assign(source="Synthetic demo")
        st.session_state.data = classify(demo_df)
        st.session_state.selected_app = {"name": "Synthetic sample", "developer": "Bundled sample data", "availability": "Synthetic data", "rating": None}
        st.session_state.fetch_counts = {"Synthetic demo": len(demo_df)}
        st.session_state.page = "Overview"

search_col, country_col, search_btn_col = st.columns([4, 1, 1.2], vertical_alignment="bottom")
with search_col:
    query = st.text_input("Application name or store URL", placeholder="Try Spotify, play.google.com/store/apps/details?id=… or apps.apple.com/…", key="app_query", help="Searches Google Play and Apple App Store public catalogs.")
with country_col:
    country = st.selectbox("Country", ["in", "us", "gb"], format_func=lambda v: {"in":"India (IN)","us":"United States (US)","gb":"United Kingdom (GB)"}[v])
with search_btn_col:
    search_clicked = st.button("Search apps", type="primary", use_container_width=True)
if search_clicked:
    if len(query.strip()) < 2:
        st.warning("Enter at least two characters, or paste a store URL.")
    else:
        try:
            with st.spinner("Searching public app stores…"):
                found = search_applications(query, country=country)
            st.session_state.search_results = found
            if not found:
                st.info("No matching applications were returned. Check the spelling or country, paste a full store URL, or use Advanced Settings.")
        except Exception as exc:
            st.error(f"App search failed: {exc}. Check your connection and retry, or use Advanced Settings.")

results = st.session_state.get("search_results", [])
if results:
    st.markdown("**Select the exact app before collecting reviews**")
    for idx, result in enumerate(results):
        name = result.get("name") or "Unnamed app"
        rating = result.get("rating")
        rating_text = f" · Store rating {rating:.1f}/5" if isinstance(rating, (int, float)) else ""
        icon = result.get("icon", "")
        icon_html = f'<img src="{icon}" alt="" />' if icon else '<span aria-hidden="true" style="font-size:30px">◉</span>'
        st.markdown(f'<div class="result">{icon_html}<div><strong>{name}</strong><br><span class="muted">{result.get("developer") or "Developer unavailable"} · {result.get("availability", result.get("store", "Store unavailable"))}{rating_text}</span></div></div>', unsafe_allow_html=True)
        if st.button(f"Select {name} · {result.get('store', 'app store')}", key=f"select_{idx}", use_container_width=True):
            st.session_state.selected_app = result
            st.session_state.selected_google = result["app_id"] if result["store"] == "Google Play" else ""
            st.session_state.selected_apple = result["app_id"] if result["store"] == "Apple App Store" else ""

selected_app = st.session_state.get("selected_app")
if selected_app and selected_app.get("availability") != "Synthetic data":
    st.success(f"Selected: {selected_app.get('name', 'Application')} · {selected_app.get('store', 'Store')}")

st.markdown('<div class="step-label">Step 2 of 4 · Choose feedback sources</div>', unsafe_allow_html=True)
source_col1, source_col2, source_col3, source_col4 = st.columns([1.1, 1.1, 1.1, 1.6], gap="small")
with source_col1:
    use_google = st.checkbox("Google Play", value=bool(st.session_state.get("selected_google")), disabled=not bool(st.session_state.get("selected_google") or manual_google), help="Select a Google Play result first, or enter its package ID in Advanced Settings.")
with source_col2:
    use_apple = st.checkbox("Apple App Store", value=bool(st.session_state.get("selected_apple")), disabled=not bool(st.session_state.get("selected_apple") or manual_apple), help="Select an Apple result first, or enter its numeric ID in Advanced Settings.")
with source_col3:
    use_csv = st.checkbox("Survey CSV", help="CSV must include text and date columns; rating is optional.")
with source_col4:
    review_count = st.slider("Google review count", 20, 200, 100, help="The Google Play scraper may return fewer reviews than requested.")
uploaded_csv = st.file_uploader("Upload survey CSV (text, date, optional rating)", type="csv", key="source_csv") if use_csv else None
st.markdown('<div class="step-label">Step 3 of 4 · Fetch and analyze</div>', unsafe_allow_html=True)
run_col, status_col = st.columns([1.35, 4], vertical_alignment="center")
with run_col:
    fetch_clicked = st.button("Fetch and analyze feedback", type="primary", use_container_width=True)
with status_col:
    st.caption("A failed source will not discard results fetched successfully from another source.")

if fetch_clicked:
    frames, counts, failures = [], {}, []
    tasks = []
    gid = st.session_state.get("selected_google") or manual_google.strip()
    aid = st.session_state.get("selected_apple") or manual_apple.strip()
    if use_google and gid:
        tasks.append(("Google Play", lambda: google_reviews(gid, country, review_count)))
    if use_apple and aid:
        tasks.append(("Apple App Store", lambda: apple_reviews(aid, country)))
    if use_csv and uploaded_csv is not None:
        tasks.append(("CSV", lambda: csv_reviews(uploaded_csv)))
    if not tasks:
        st.warning("Choose at least one available feedback source. Select an app first, enter an ID in Advanced Settings, or upload a CSV.")
    else:
        progress = st.progress(0, text="Starting feedback collection…")
        for task_idx, (source_name, fn) in enumerate(tasks, start=1):
            try:
                with st.spinner(f"Fetching {source_name} reviews…"):
                    frame = fn()
                counts[source_name] = len(frame)
                if not frame.empty:
                    frames.append(frame)
                else:
                    failures.append(f"{source_name}: the store returned no usable reviews.")
            except Exception as exc:
                failures.append(f"{source_name}: {str(exc)[:220]}")
            progress.progress(task_idx / len(tasks), text=f"Checked {source_name} ({counts.get(source_name, 0)} reviews)")
        if frames:
            fresh = classify(pd.concat(frames, ignore_index=True).drop_duplicates(["source", "text", "date"]))
            if "data" in st.session_state:
                old = st.session_state.data
                combined = pd.concat([old, fresh], ignore_index=True).drop_duplicates(["source", "text", "date"], keep="last")
                st.session_state.data = combined
            else:
                st.session_state.data = fresh
            st.session_state.fetch_counts = counts
            st.session_state.page = "Overview"
            st.success(f"Analysis complete. Successfully collected {sum(counts.values())} review(s) across {sum(n > 0 for n in counts.values())} source(s).")
        else:
            st.error("No new reviews were collected. Existing results have been preserved. Check the selected app and country, review source access, or try a CSV.")
        for message in failures:
            st.warning(message + " You can retry this source while keeping successful partial results.")

if "data" not in st.session_state:
    st.markdown("<div class='section-sub'>Step 4 appears here after your first analysis. No sample data is loaded unless you choose the synthetic demo.</div>", unsafe_allow_html=True)
    st.stop()

st.markdown('<div class="step-label">Step 4 of 4 · Explore insights and download reports</div>', unsafe_allow_html=True)
nav = st.radio("Dashboard sections", ["Overview", "Reviews", "Insights", "Reports"], horizontal=True, key="page", label_visibility="collapsed")
df = st.session_state.data.copy()
if "date" in df:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

with st.expander("Filter feedback", expanded=True):
    source_options = sorted(df.source.dropna().unique())
    sentiments = ["Positive", "Neutral", "Negative"]
    min_date = df.date.min().date()
    max_date = df.date.max().date()
    f1, f2, f3, f4 = st.columns([1.1, 1.2, 1.4, 1.4], gap="small")
    with f1: source_filter = st.multiselect("Source", source_options, default=source_options)
    with f2: sentiment_filter = st.multiselect("Sentiment", sentiments, default=sentiments)
    with f3: dates = st.date_input("Date range", (min_date, max_date))
    with f4: query_filter = st.text_input("Search review text", placeholder="Search words or phrases")
    rating_min, rating_max = st.slider("Rating range", 1, 5, (1, 5), help="Filters store or survey ratings from 1 to 5.")
filtered = filter_reviews(df, sources=source_filter, sentiments=sentiment_filter, date_range=dates if len(dates) == 2 else None,
                          rating_range=(rating_min, rating_max), query=query_filter)
if filtered.empty:
    st.info("No reviews match these filters. Widen the date or rating range, select more sources or sentiments, or clear the search text.")
    st.stop()

if nav in ("Overview", "Insights"):
    st.markdown('<div class="section-title">Performance snapshot</div><div class="section-sub">Sentiment describes the review text. Average rating is the original user-provided store or survey rating.</div>', unsafe_allow_html=True)
    n_reviews = len(filtered)
    avg_rating = filtered.rating.dropna().mean()
    positive = filtered.sentiment.eq("Positive").mean()
    negative = filtered.sentiment.eq("Negative").mean()
    neutral = filtered.sentiment.eq("Neutral").mean()
    kpis = st.columns(5, gap="small")
    kpis[0].metric("Total reviews", f"{n_reviews:,}")
    kpis[1].metric("Average rating", f"{avg_rating:.2f} / 5" if pd.notna(avg_rating) else "Not provided")
    kpis[2].metric("Positive sentiment", f"{positive:.0%}")
    kpis[3].metric("Negative sentiment", f"{negative:.0%}")
    kpis[4].metric("Neutral sentiment", f"{neutral:.0%}")
    st.markdown('<div class="section-title">Sentiment distribution and historical trends</div>', unsafe_allow_html=True)
    chart_left, chart_right = st.columns([1, 1.5], gap="medium")
    palette = {"Positive":"#70d6a0", "Neutral":"#a7adba", "Negative":"#ff827c"}
    with chart_left:
        with st.container(border=True):
            st.markdown("**Sentiment distribution**")
            dist = filtered.sentiment.value_counts().reindex(sentiments, fill_value=0).rename_axis("Sentiment").reset_index(name="Reviews")
            pie = px.pie(dist, names="Sentiment", values="Reviews", hole=.65, color="Sentiment", color_discrete_map=palette)
            pie.update_layout(height=290, margin=dict(l=4,r=4,t=10,b=4), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f5f5f7"), legend=dict(orientation="h",y=-.05))
            st.plotly_chart(pie, use_container_width=True, config={"displayModeBar":False}, key="sentiment_chart")
            st.dataframe(dist, use_container_width=True, hide_index=True, key="distribution_table")
    with chart_right:
        with st.container(border=True):
            st.markdown("**Daily sentiment trend**")
            trend_df = trends(filtered)
            line = px.line(trend_df, x="day", y="mean", markers=True, custom_data=["count"], labels={"day":"Date","mean":"Average sentiment","count":"Review count"})
            line.update_traces(line=dict(color="#8ab8ff",width=3), hovertemplate="%{x|%b %d}<br>Sentiment score: %{y:.2f}<br>Reviews: %{customdata[0]}<extra></extra>")
            line.update_layout(height=290,margin=dict(l=5,r=5,t=10,b=5),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#c0c1c8"),yaxis=dict(range=[-1,1],gridcolor="rgba(161,161,170,.18)",title="Average sentiment (−1 to +1)"),xaxis=dict(title="Date"),showlegend=False)
            st.plotly_chart(line,use_container_width=True,config={"displayModeBar":False},key="trend_chart")
            st.dataframe(trend_df.rename(columns={"day":"Date","mean":"Average sentiment","count":"Reviews"}),use_container_width=True,hide_index=True,key="trend_table")
    st.markdown('<div class="section-title">Recurring complaints and prioritized issues</div><div class="section-sub">Keyword-based themes from negative feedback, ranked by estimated impact.</div>', unsafe_allow_html=True)
    issue_df = issues(filtered)
    if issue_df.empty:
        st.info("No recognized recurring complaint themes were found in these negative reviews. Review the comments table for other issues.")
    else:
        st.dataframe(issue_df.rename(columns={"issue":"Issue theme","frequency":"Mentions","priority":"Priority score"}),use_container_width=True,hide_index=True)
elif nav == "Reviews":
    st.markdown('<div class="section-title">Review explorer</div><div class="section-sub">Search is applied above along with source, date, rating, and sentiment filters.</div>', unsafe_allow_html=True)
    st.caption("Sentiment strength is the VADER component associated with the assigned label. It is not calibrated model confidence or a probability.")
    review_view = filtered.sort_values("date",ascending=False).copy()
    review_view["date"] = review_view["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(review_view,use_container_width=True,hide_index=True,height=520,column_config={"score":st.column_config.NumberColumn("VADER sentiment score",format="%+.2f"),"confidence":st.column_config.ProgressColumn("Sentiment strength (not confidence)",min_value=0,max_value=1,format="%.0%%"),"rating":st.column_config.NumberColumn("User rating",format="%.1f / 5")})
elif nav == "Insights":
    st.info("The KPI cards, accessible chart tables, trend, complaints, and prioritized issues are available in Overview.")
elif nav == "Reports":
    st.markdown('<div class="section-title">Reports and exports</div><div class="section-sub">Exports include only the feedback matching the current filters.</div>', unsafe_allow_html=True)
    st.caption(f"PDF report covers the seven days ending {filtered.date.max().date()} and summarizes {len(filtered)} filtered review(s).")
    pdf_data = weekly_pdf(filtered)
    csv_data = filtered.to_csv(index=False).encode("utf-8-sig")
    d1,d2 = st.columns(2)
    with d1: st.download_button("Download weekly PDF report",pdf_data,"signal_weekly_feedback.pdf","application/pdf",use_container_width=True)
    with d2: st.download_button("Download analyzed CSV",csv_data,"signal_feedback.csv","text/csv",use_container_width=True)
    st.markdown("**Source results this session**")
    st.dataframe(pd.DataFrame([{"Source":key,"Reviews fetched":value} for key,value in st.session_state.get("fetch_counts",{}).items()]),use_container_width=True,hide_index=True)

st.markdown("<div style='height:24px;border-bottom:1px solid #41444d;margin-bottom:14px'></div><span class='muted'>Signal · VADER sentiment analysis · Store reviews are subject to third-party availability and limits.</span>",unsafe_allow_html=True)
