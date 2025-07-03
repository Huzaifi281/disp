import streamlit as st
import pandas as pd
import os
import base64
import time

# ---------------------- Page Config ----------------------
st.set_page_config(page_title="📄 Disputed Transactions", layout="wide")

# ---------------------- Load Data ------------------------
@st.cache_data
def load_data():
    return pd.read_excel("disputed.xlsx")

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

# ---------------------- Title and Header ----------------------
st.title("📄 Disputed Transactions Report")

st.markdown("""
<style>
.sticky-action {
    position: sticky;
    top: 0;
    background: white;
    z-index: 999;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #eee;
    font-size: 1rem;
    font-weight: bold;
    color: #0e76a8;
}
.metric-card {
    background-color: #f0f4f8;
    padding: 1.5rem;
    border-radius: 1.25rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    text-align: center;
    margin-bottom: 1rem;
}
.metric-label {
    font-size: 1.1rem;
    color: #555;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 600;
    color: #0e76a8;
}
</style>

<div class='sticky-action'>📊 Review & Match Disputed PDFs with Transactions</div>
""", unsafe_allow_html=True)

st.markdown("""
This dashboard provides a professional summary and details of disputed transactions.
Use the filters to drill down to specific entries and review discrepancies effectively.
""")

# ---------------------- Summary Metrics ----------------------
total_disputed_amount = df["Amt"].sum() if "Amt" in df.columns else 0
total_disputed_count = len(df)

df["Date"] = pd.to_datetime(df["Date"])  # Ensure datetime format
min_date = df["Date"].min()
max_date = df["Date"].max()
date_fmt = '%#d %b %Y' if os.name == 'nt' else '%-d %b %Y'
date_range_str = f"{min_date.strftime(date_fmt)} → {max_date.strftime(date_fmt)}"

# Show metrics (stacked vertically for mobile responsiveness)
for label, value, icon in [
    ("Total Disputed Amount", f"${total_disputed_amount:,.2f}", "💰"),
    ("Total Disputed Transactions", total_disputed_count, "🔢"),
    ("Date Range", date_range_str, "🕒")
]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------- Daily Transaction Details ----------------------
st.markdown("### 📂 Related PDF Documents by Date")

pdf_dir = "data"
available_pdfs = {f.replace(".pdf", ""): f for f in os.listdir(pdf_dir) if f.endswith(".pdf")}

dates_in_data = sorted(df["Date"].dt.date.unique())
total_dates = len(dates_in_data)

# Progress bar start
pdf_progress = st.progress(0, text="🔄 Initializing PDF document loading...")

for i, tx_date in enumerate(dates_in_data):
    progress_percent = (i + 1) / total_dates
    pretty_display = tx_date.strftime(date_fmt)
    display_key = tx_date.strftime('%#d %b') if os.name == 'nt' else tx_date.strftime('%-d %b')

    pdf_progress.progress(progress_percent, text=f"📅 Loading {pretty_display}...")

    # Get data for this date
    day_df = df[df["Date"].dt.date == tx_date]
    day_total = day_df["Amt"].sum() if "Amt" in day_df.columns else 0
    txn_count = len(day_df)

    expander_title = f"📅 {pretty_display} — 💰 ${day_total:,.2f} | 🧾 {txn_count} txns"

    with st.expander(expander_title, expanded=False):
        st.markdown(f"**🔹 Transactions on {pretty_display}:**")
        st.dataframe(
            day_df.reset_index(drop=True).style.format({'Amt': '{:,.2f}'}),
            use_container_width=True
        )

        # Embed PDF if found
        if display_key in available_pdfs:
            pdf_path = os.path.join(pdf_dir, available_pdfs[display_key])
            try:
                with open(pdf_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                    st.download_button(
                        label="📄 Download PDF of having Disputed Trans",
                        data=base64.b64decode(base64_pdf),
                        file_name=available_pdfs[display_key],
                        mime="application/pdf"
                    )

            except Exception as e:
                st.error(f"❌ Error loading PDF: {e}")
        else:
            st.warning("🚫 No PDF found for this date.")

    time.sleep(0.1)  # Simulate load delay for UX

# Done
pdf_progress.empty()
st.success("✅ All daily summaries and PDFs loaded successfully.")
