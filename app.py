import io
import streamlit as st
import pandas as pd
from report_generator import process_data, generate_pdf
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────
st.set_page_config(
    page_title="AutoReport — Banking Financial Report Generator",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ────────────────────────────────────
st.markdown("""
<style>
  /* Global */
  body, .stApp { background-color: #F0F4F8; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B4F72 0%, #2E86C1 100%);
  }
  [data-testid="stSidebar"] * { color: white !important; }
  [data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.15) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
  }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    border: 1px solid #AED6F1;
    box-shadow: 0 2px 8px rgba(27,79,114,0.08);
  }
  [data-testid="metric-container"] label {
    color: #7F8C8D !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #1B4F72 !important;
    font-size: 22px !important;
    font-weight: 700 !important;
  }

  /* Headers */
  h1 { color: #1B4F72 !important; }
  h2, h3 { color: #2E86C1 !important; }

  /* Download button */
  .stDownloadButton button {
    background: linear-gradient(135deg, #1B4F72, #2E86C1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity 0.2s !important;
  }
  .stDownloadButton button:hover { opacity: 0.88 !important; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #EBF5FB;
    border-radius: 10px;
    padding: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    color: #1B4F72;
  }
  .stTabs [aria-selected="true"] {
    background: white !important;
    color: #1B4F72 !important;
  }

  /* Dataframe */
  [data-testid="stDataFrame"] { border-radius: 10px; }

  /* Section cards */
  .section-card {
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    border: 1px solid #AED6F1;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(27,79,114,0.06);
  }
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 AutoReport")
    st.markdown("**Banking Financial Report Generator**")
    st.markdown("---")

    st.markdown("### ⚙️ Report Settings")

    bank_name = st.text_input(
        "Bank / Organization Name",
        value="Gadaa Bank S.C",
        placeholder="Enter bank name...",
    )

    report_period = st.text_input(
        "Report Period",
        value=f"H1 {datetime.now().year}",
        placeholder="e.g. Q1 2026, January–June 2026",
    )

    st.markdown("---")
    st.markdown("### 📁 Upload Data")
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Upload your branch performance data",
    )

    st.markdown("---")
    st.markdown("### 📋 Required Columns")
    cols = [
        "Branch", "Month", "Total_Deposits", "Total_Loans",
        "NPL_Amount", "Interest_Income", "Operating_Expenses",
        "New_Customers", "Loan_Approvals", "Loan_Rejections",
    ]
    for col in cols:
        st.markdown(f"• `{col}`")

    st.markdown("---")
    st.markdown("### 📥 Sample Data")
    with open("sample_data.csv", "rb") as f:
        st.download_button(
            "⬇ Download Sample CSV",
            f.read(),
            "sample_banking_data.csv",
            "text/csv",
        )

    st.markdown("---")
    st.markdown(
        "<small>Built with Python · Pandas · ReportLab · Streamlit<br/>"
        "by Amanuel Adamu</small>",
        unsafe_allow_html=True,
    )


# ── MAIN CONTENT ──────────────────────────────────
st.markdown("# 🏦 AutoReport — Banking Financial Report Generator")
st.markdown(
    "Upload your branch performance data to instantly generate a "
    "**professional PDF financial report** with charts, KPIs, and recommendations."
)
st.markdown("---")

if uploaded_file is None:
    # Landing state
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="section-card" style="text-align:center">
          <div style="font-size:36px">📤</div>
          <h3 style="color:#1B4F72">Upload Data</h3>
          <p style="color:#7F8C8D;font-size:14px">Upload your CSV or Excel file with branch performance data</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="section-card" style="text-align:center">
          <div style="font-size:36px">📊</div>
          <h3 style="color:#1B4F72">Instant Analysis</h3>
          <p style="color:#7F8C8D;font-size:14px">KPIs, charts, and branch comparisons generated automatically</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="section-card" style="text-align:center">
          <div style="font-size:36px">📄</div>
          <h3 style="color:#1B4F72">Download PDF</h3>
          <p style="color:#7F8C8D;font-size:14px">Professional multi-page PDF report ready in seconds</p>
        </div>
        """, unsafe_allow_html=True)

    st.info(
        "👈 Upload your data file using the sidebar, or download the **Sample CSV** "
        "to try the report generator immediately."
    )

else:
    # Load data
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        required = [
            "Branch", "Month", "Total_Deposits", "Total_Loans",
            "NPL_Amount", "Interest_Income", "Operating_Expenses",
            "New_Customers", "Loan_Approvals", "Loan_Rejections",
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            st.error(f"❌ Missing columns: {', '.join(missing)}")
            st.stop()

        data = process_data(df)

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.stop()

    # ── SUCCESS BANNER ────────────────────────────
    st.success(
        f"✅ Data loaded successfully — **{len(df)} records** across "
        f"**{len(data['branches'])} branches**"
    )

    # ── KPI METRICS ───────────────────────────────
    st.markdown("## 📊 Key Performance Indicators")

    def fmt_etb(val):
        if val >= 1_000_000:
            return f"ETB {val/1_000_000:.2f}M"
        elif val >= 1_000:
            return f"ETB {val/1_000:.1f}K"
        return f"ETB {val:,.0f}"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Deposits",   fmt_etb(data["total_deposits"]))
    c2.metric("🏦 Total Loans",      fmt_etb(data["total_loans"]))
    c3.metric("⚠️ Total NPL",        fmt_etb(data["total_npl"]))
    c4.metric("📈 Net Income",       fmt_etb(data["net_income"]))

    c5, c6, c7, c8 = st.columns(4)
    npl_delta = "⚠️ Above Warning" if data["npl_ratio"] > 3 else "✅ Healthy"
    c5.metric("NPL Ratio",         f"{data['npl_ratio']:.2f}%",    npl_delta)
    c6.metric("Loan-to-Deposit",   f"{data['loan_to_deposit']:.1f}%")
    c7.metric("New Customers",     f"{data['total_customers']:,}")
    c8.metric("Approval Rate",     f"{data['approval_rate']:.1f}%")

    st.markdown("---")

    # ── TABS ──────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏢 Branch Analysis",
        "📅 Monthly Trends",
        "🥧 Portfolio",
        "📋 Raw Data",
    ])

    with tab1:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        bs = data["branch_summary"]

        fig, ax = plt.subplots(figsize=(10, 4.5))
        x = np.arange(len(bs["Branch"]))
        w = 0.38
        ax.bar(x - w/2, bs["Total_Deposits"]/1e6, w, label="Deposits",
               color="#1B4F72", alpha=0.88)
        ax.bar(x + w/2, bs["Total_Loans"]/1e6, w, label="Loans",
               color="#F39C12", alpha=0.88)
        ax.set_xticks(x)
        ax.set_xticklabels(bs["Branch"])
        ax.set_title("Deposits vs Loans by Branch (ETB Millions)", fontweight="bold")
        ax.set_ylabel("ETB Millions")
        ax.legend()
        ax.yaxis.grid(True, alpha=0.4)
        ax.set_facecolor("#FAFAFA")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        st.markdown("#### NPL Ratio by Branch")
        fig2, ax2 = plt.subplots(figsize=(10, 3.5))
        bs_sorted = bs.sort_values("NPL_Ratio", ascending=True)
        colors_bar = ["#C0392B" if r > 5 else "#F39C12" if r > 3 else "#1E8449"
                      for r in bs_sorted["NPL_Ratio"]]
        ax2.barh(bs_sorted["Branch"], bs_sorted["NPL_Ratio"],
                 color=colors_bar, alpha=0.88, height=0.5)
        ax2.axvline(5, color="#C0392B", linestyle="--", linewidth=1.2,
                    label="Critical (5%)", alpha=0.7)
        ax2.axvline(3, color="#F39C12", linestyle="--", linewidth=1.2,
                    label="Warning (3%)", alpha=0.7)
        ax2.set_title("NPL Ratio by Branch (%)", fontweight="bold")
        ax2.set_xlabel("NPL Ratio (%)")
        ax2.legend(fontsize=8)
        ax2.xaxis.grid(True, alpha=0.4)
        ax2.set_facecolor("#FAFAFA")
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    with tab2:
        ms = data["month_summary"]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))

        ax1.plot(ms["Month"].astype(str), ms["Total_Deposits"]/1e6,
                 marker="o", color="#1B4F72", linewidth=2, label="Deposits")
        ax1.plot(ms["Month"].astype(str), ms["Total_Loans"]/1e6,
                 marker="s", color="#F39C12", linewidth=2, label="Loans")
        ax1.fill_between(ms["Month"].astype(str),
                         ms["Total_Deposits"]/1e6, alpha=0.08, color="#1B4F72")
        ax1.set_title("Monthly Deposit & Loan Trends", fontweight="bold")
        ax1.set_ylabel("ETB Millions")
        ax1.tick_params(axis="x", rotation=30)
        ax1.legend()
        ax1.yaxis.grid(True, alpha=0.4)
        ax1.set_facecolor("#FAFAFA")

        ax2.bar(ms["Month"].astype(str), ms["New_Customers"],
                color="#2E86C1", alpha=0.85)
        ax2.set_title("Monthly New Customer Acquisition", fontweight="bold")
        ax2.set_ylabel("New Customers")
        ax2.tick_params(axis="x", rotation=30)
        ax2.yaxis.grid(True, alpha=0.4)
        ax2.set_facecolor("#FAFAFA")

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with tab3:
        col_a, col_b = st.columns(2)
        with col_a:
            fig, ax = plt.subplots(figsize=(5, 5))
            sizes = [data["total_approvals"], data["total_rejections"]]
            labels = [f"Approved\n{data['total_approvals']:,}",
                      f"Rejected\n{data['total_rejections']:,}"]
            ax.pie(sizes, labels=labels, colors=["#1E8449", "#C0392B"],
                   autopct="%1.1f%%", startangle=90, explode=(0.04, 0),
                   wedgeprops={"edgecolor": "white", "linewidth": 2})
            ax.set_title("Loan Approval Rate", fontweight="bold")
            st.pyplot(fig)
            plt.close(fig)

        with col_b:
            fig, ax = plt.subplots(figsize=(5, 5))
            bs = data["branch_summary"]
            palette = ["#1B4F72", "#2E86C1", "#F39C12", "#1E8449", "#C0392B"]
            ax.pie(bs["Total_Deposits"], labels=bs["Branch"],
                   colors=palette[:len(bs)], autopct="%1.1f%%",
                   startangle=140,
                   wedgeprops={"edgecolor": "white", "linewidth": 2})
            ax.set_title("Deposit Distribution by Branch", fontweight="bold")
            st.pyplot(fig)
            plt.close(fig)

    with tab4:
        st.markdown("#### 📋 Branch Summary")
        st.dataframe(
            data["branch_summary"].style.format({
                "Total_Deposits": "{:,.0f}",
                "Total_Loans": "{:,.0f}",
                "NPL_Amount": "{:,.0f}",
                "NPL_Ratio": "{:.2f}%",
                "Interest_Income": "{:,.0f}",
                "Operating_Expenses": "{:,.0f}",
                "Net_Income": "{:,.0f}",
                "New_Customers": "{:,.0f}",
                "Loan_Approvals": "{:,.0f}",
                "Loan_Rejections": "{:,.0f}",
            }),
            use_container_width=True,
        )

        st.markdown("#### 📋 Raw Data")
        st.dataframe(df, use_container_width=True)

    # ── GENERATE PDF ──────────────────────────────
    st.markdown("---")
    st.markdown("## 📄 Generate PDF Report")

    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown(
            "Click the button to generate a **professional multi-page PDF report** "
            "including all charts, KPI cards, branch summary table, and recommendations."
        )
    with col_right:
        if st.button("⚡ Generate Report", type="primary", use_container_width=True):
            with st.spinner("Generating PDF report..."):
                try:
                    pdf_bytes = generate_pdf(data, bank_name, report_period)
                    filename = (
                        f"{bank_name.replace(' ', '_')}_"
                        f"{report_period.replace(' ', '_')}_Report.pdf"
                    )
                    st.success("✅ Report generated successfully!")
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"❌ Error generating report: {e}")