import streamlit as st
import pandas as pd, os, json
from agents.collector import collect_and_deduplicate
from agents.enricher import enrich_with_crm
from agents.categorizer import categorize_feedback
from agents.scorer import compute_priority_scores
from agents.reporter import generate_weekly_report

st.set_page_config(page_title="Feedback Prioritizer (Offline Demo)", layout="wide")
st.title("Customer Feedback Prioritizer — Offline Streamlit Demo")

DATA_DIR = "data"
DELIVERIES = "deliveries"
os.makedirs(DELIVERIES, exist_ok=True)

st.sidebar.header("Quick actions")
sample_fb = st.sidebar.checkbox("Load sample feedback on startup", value=True)
if sample_fb:
    fb_df = pd.read_csv(os.path.join(DATA_DIR, "sample_feedback.csv"))
else:
    fb_df = pd.DataFrame()

uploaded = st.file_uploader("Upload feedback CSV (columns: raw_text, source, customer_email (optional), created_at)", type=["csv"])
if uploaded is not None:
    fb_df = pd.read_csv(uploaded)

st.header("1. Raw / Uploaded Feedback")
st.write("Preview (first 50 rows)")
st.dataframe(fb_df.head(50))

if st.button("Run Agent 1: Collect & Deduplicate"):
    dedup = collect_and_deduplicate(fb_df)
    dedup.to_csv(os.path.join(DELIVERIES, "deduplicated_feedback.csv"), index=False)
    st.success(f"Deduplication finished. {len(dedup)} records saved to deliveries/deduplicated_feedback.csv")
    st.dataframe(dedup.head(50))

st.write("---")
st.header("2. Enrich with CRM / Revenue Data (Agent 2)")
crm_uploaded = st.file_uploader("Upload CRM CSV (columns: customer_email, company, mrr, tier, renewal_date)", type=["csv"], key="crm")
if crm_uploaded is not None:
    crm_df = pd.read_csv(crm_uploaded)
else:
    crm_df = pd.read_csv(os.path.join(DATA_DIR, "sample_crm.csv"))

st.write("CRM sample")
st.dataframe(crm_df.head(20))

if st.button("Run Agent 2: Enrich"):
    # read latest dedup or use uploaded
    dedup_path = os.path.join(DELIVERIES, "deduplicated_feedback.csv")
    if os.path.exists(dedup_path):
        dedup = pd.read_csv(dedup_path)
    else:
        dedup = fb_df.copy()
    enriched = enrich_with_crm(dedup, crm_df)
    enriched.to_csv(os.path.join(DELIVERIES, "enriched_feedback.csv"), index=False)
    st.success(f"Enrichment finished. {len(enriched)} records saved to deliveries/enriched_feedback.csv")
    st.dataframe(enriched.head(50))

st.write("---")
st.header("3. Categorize Feedback (Agent 3)")
if st.button("Run Agent 3: Categorize"):
    enriched_path = os.path.join(DELIVERIES, "enriched_feedback.csv")
    if os.path.exists(enriched_path):
        enriched = pd.read_csv(enriched_path)
    else:
        st.error("Enriched file not found. Run Agent 2 first or upload data.")
        st.stop()
    categorized = categorize_feedback(enriched)
    categorized.to_csv(os.path.join(DELIVERIES, "categorized_feedback.csv"), index=False)
    st.success("Categorization finished and saved to deliveries/categorized_feedback.csv")
    st.dataframe(categorized.head(50))

st.write("---")
st.header("4. Priority Scoring (Agent 4)")
if st.button("Run Agent 4: Score Priorities"):
    cat_path = os.path.join(DELIVERIES, "categorized_feedback.csv")
    if os.path.exists(cat_path):
        cat = pd.read_csv(cat_path)
    else:
        st.error("Categorized file not found. Run Agent 3 first.")
        st.stop()
    scored = compute_priority_scores(cat)
    scored.to_csv(os.path.join(DELIVERIES, "scored_feedback.csv"), index=False)
    st.success("Scoring finished and saved to deliveries/scored_feedback.csv")
    st.dataframe(scored.sort_values("priority_score", ascending=False).head(30))

st.write("---")
st.header("5. Insight Generation & Delivery (Agent 5)")
weekly_title = st.text_input("Weekly Report Title", value="Weekly Feedback Priorities — Demo")
if st.button("Run Agent 5: Generate Report & Deliver"):
    scored_path = os.path.join(DELIVERIES, "scored_feedback.csv")
    if not os.path.exists(scored_path):
        st.error("Scored file not found. Run Agent 4 first.")
        st.stop()
    scored = pd.read_csv(scored_path)
    report_files = generate_weekly_report(scored, title=weekly_title, outdir=DELIVERIES)
    st.success("Report generated and saved to deliveries/")
    for p in report_files:
        st.write(p)
    st.markdown("**Simulated deliveries:** Notion → markdown file, Slack → message files, Email → markdown files in `deliveries/`")

st.write("---")
st.header("Export / Download")
if st.button("Create ZIP of project outputs"):
    zip_path = "deliveries_outputs.zip"
    import zipfile, os
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for folder,_,files in os.walk("deliveries"):
            for f in files:
                zf.write(os.path.join(folder,f))
    st.success(f"Created {zip_path} in project root. You can download it from the working folder.")

st.info("Everything runs locally and is saved under the `deliveries/` folder. You can inspect CSVs and markdowns directly.")
