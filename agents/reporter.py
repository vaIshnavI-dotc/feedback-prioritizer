import pandas as pd, os
def generate_weekly_report(df, title="Weekly Feedback Priorities", outdir="deliveries"):
    os.makedirs(outdir, exist_ok=True)
    top = df.sort_values("priority_score", ascending=False).head(10)
    total_risk = df['customer_mrr'].sum()
    md = []
    md.append(f"# {title}\n")
    md.append("## Executive Summary\n")
    md.append(f"- Top items this week: {len(top)}\n")
    md.append(f"- Total revenue represented in dataset: ${total_risk:,.2f}\n")
    md.append("\n### Top 10 prioritized issues\n")
    for _, row in top.iterrows():
        md.append(f"**Score {row['priority_score']}** — {row['raw_text']}\n\n - Company: {row.get('customer_company','Unknown')}, MRR: {row.get('customer_mrr',0)}\n - Category: {row.get('category_type','')}/{row.get('category_area','')}\n - Sentiment: {row.get('sentiment','')}\n - Urgency keywords: {row.get('urgency_keywords','')}\n\n")
    md.append("\n## Categorized breakdown\n")
    bytype = df['category_type'].value_counts().to_dict()
    for k,v in bytype.items():
        md.append(f"- {k}: {v}\n")
    # Save markdown
    md_path = os.path.join(outdir, "weekly_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\\n".join(md))
    # Simulate Notion: copy markdown to notion_page.md
    notion_path = os.path.join(outdir, "notion_weekly_page.md")
    with open(notion_path, "w", encoding="utf-8") as f:
        f.write("# Notion-simulated page\\n\\n")
        f.write("\\n".join(md))
    # Simulate Slack message (json)
    slack_msg = {"channel":"#product-feedback", "text": f"{title} — Top item: {top.iloc[0]['raw_text'] if len(top)>0 else 'N/A'}"}
    slack_path = os.path.join(outdir, "slack_message.json")
    import json
    with open(slack_path, "w", encoding="utf-8") as f:
        json.dump(slack_msg, f, indent=2)
    # Save CSVs for exports
    df.to_csv(os.path.join(outdir, "scored_feedback_export.csv"), index=False)
    return [md_path, notion_path, slack_path, os.path.join(outdir, "scored_feedback_export.csv")]
