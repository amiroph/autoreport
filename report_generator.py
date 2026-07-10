import io
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable, KeepTogether, PageBreak,
)
from datetime import datetime

# ── BRAND COLORS ──────────────────────────────────
PRIMARY    = "#1B4F72"   # deep blue
SECONDARY  = "#2E86C1"  # medium blue
ACCENT     = "#F39C12"  # gold/amber
SUCCESS    = "#1E8449"  # green
DANGER     = "#C0392B"  # red
LIGHT_BG   = "#EBF5FB"  # light blue bg
DARK_TEXT  = "#1A252F"  # near black

# ReportLab colors
RL_PRIMARY   = colors.HexColor(PRIMARY)
RL_SECONDARY = colors.HexColor(SECONDARY)
RL_ACCENT    = colors.HexColor(ACCENT)
RL_SUCCESS   = colors.HexColor(SUCCESS)
RL_DANGER    = colors.HexColor(DANGER)
RL_LIGHT     = colors.HexColor(LIGHT_BG)
RL_WHITE     = colors.white
RL_GRAY      = colors.HexColor("#7F8C8D")
RL_LIGHT_GRAY = colors.HexColor("#ECF0F1")


# ── DATA PROCESSING ───────────────────────────────
def process_data(df: pd.DataFrame) -> dict:
    df = df.copy()
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]

    # Ensure numeric columns
    numeric_cols = [
        "Total_Deposits", "Total_Loans", "NPL_Amount",
        "Interest_Income", "Operating_Expenses",
        "New_Customers", "Loan_Approvals", "Loan_Rejections",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # KPIs
    total_deposits      = df["Total_Deposits"].sum()
    total_loans         = df["Total_Loans"].sum()
    total_npl           = df["NPL_Amount"].sum()
    total_income        = df["Interest_Income"].sum()
    total_expenses      = df["Operating_Expenses"].sum()
    total_customers     = df["New_Customers"].sum()
    total_approvals     = df["Loan_Approvals"].sum()
    total_rejections    = df["Loan_Rejections"].sum()

    npl_ratio           = (total_npl / total_loans * 100) if total_loans > 0 else 0
    loan_to_deposit     = (total_loans / total_deposits * 100) if total_deposits > 0 else 0
    net_income          = total_income - total_expenses
    cost_to_income      = (total_expenses / total_income * 100) if total_income > 0 else 0
    approval_rate       = (total_approvals / (total_approvals + total_rejections) * 100) if (total_approvals + total_rejections) > 0 else 0

    # By branch
    branch_summary = df.groupby("Branch").agg(
        Total_Deposits=("Total_Deposits", "sum"),
        Total_Loans=("Total_Loans", "sum"),
        NPL_Amount=("NPL_Amount", "sum"),
        Interest_Income=("Interest_Income", "sum"),
        Operating_Expenses=("Operating_Expenses", "sum"),
        New_Customers=("New_Customers", "sum"),
        Loan_Approvals=("Loan_Approvals", "sum"),
        Loan_Rejections=("Loan_Rejections", "sum"),
    ).reset_index()
    branch_summary["NPL_Ratio"] = (
        branch_summary["NPL_Amount"] / branch_summary["Total_Loans"] * 100
    ).round(2)
    branch_summary["Net_Income"] = (
        branch_summary["Interest_Income"] - branch_summary["Operating_Expenses"]
    )

    # By month
    month_order = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December",
    ]
    month_summary = df.groupby("Month").agg(
        Total_Deposits=("Total_Deposits", "sum"),
        Total_Loans=("Total_Loans", "sum"),
        NPL_Amount=("NPL_Amount", "sum"),
        Interest_Income=("Interest_Income", "sum"),
        New_Customers=("New_Customers", "sum"),
    ).reset_index()
    month_summary["Month"] = pd.Categorical(
        month_summary["Month"], categories=month_order, ordered=True
    )
    month_summary = month_summary.sort_values("Month")

    return {
        "df": df,
        "total_deposits":   total_deposits,
        "total_loans":      total_loans,
        "total_npl":        total_npl,
        "total_income":     total_income,
        "total_expenses":   total_expenses,
        "total_customers":  int(total_customers),
        "total_approvals":  int(total_approvals),
        "total_rejections": int(total_rejections),
        "npl_ratio":        round(npl_ratio, 2),
        "loan_to_deposit":  round(loan_to_deposit, 2),
        "net_income":       net_income,
        "cost_to_income":   round(cost_to_income, 2),
        "approval_rate":    round(approval_rate, 2),
        "branch_summary":   branch_summary,
        "month_summary":    month_summary,
        "branches":         df["Branch"].unique().tolist(),
        "months":           month_summary["Month"].tolist(),
    }


# ── CHART GENERATORS ──────────────────────────────
def set_chart_style():
    plt.rcParams.update({
        "font.family":     "DejaVu Sans",
        "font.size":       9,
        "axes.titlesize":  11,
        "axes.titleweight":"bold",
        "axes.titlecolor": DARK_TEXT,
        "axes.labelcolor": DARK_TEXT,
        "axes.edgecolor":  "#BDC3C7",
        "axes.linewidth":  0.8,
        "xtick.color":     "#7F8C8D",
        "ytick.color":     "#7F8C8D",
        "grid.color":      "#ECF0F1",
        "grid.linewidth":  0.6,
        "figure.facecolor":"white",
        "axes.facecolor":  "white",
    })


def fig_to_image(fig, width_cm=16, height_cm=8):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    buf.seek(0)
    plt.close(fig)
    img = Image(buf, width=width_cm * cm, height=height_cm * cm)
    return img


def chart_deposits_vs_loans(data: dict):
    set_chart_style()
    bs = data["branch_summary"]
    x = np.arange(len(bs["Branch"]))
    w = 0.38

    fig, ax = plt.subplots(figsize=(10, 5))
    bars1 = ax.bar(x - w/2, bs["Total_Deposits"] / 1e6, w,
                   label="Total Deposits", color=PRIMARY, alpha=0.88, zorder=3)
    bars2 = ax.bar(x + w/2, bs["Total_Loans"] / 1e6, w,
                   label="Total Loans", color=ACCENT, alpha=0.88, zorder=3)

    ax.set_title("Deposits vs Loans by Branch (ETB Millions)")
    ax.set_xticks(x)
    ax.set_xticklabels(bs["Branch"], fontsize=9)
    ax.set_ylabel("Amount (ETB Millions)")
    ax.yaxis.grid(True, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(framealpha=0.9, fontsize=9)

    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{bar.get_height():.1f}M", ha="center", va="bottom",
                fontsize=7.5, color=PRIMARY, fontweight="bold")
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{bar.get_height():.1f}M", ha="center", va="bottom",
                fontsize=7.5, color="#9A7D0A", fontweight="bold")

    fig.tight_layout()
    return fig_to_image(fig, 16, 7)


def chart_npl_ratio(data: dict):
    set_chart_style()
    bs = data["branch_summary"].sort_values("NPL_Ratio", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 4))
    colors_bar = [DANGER if r > 5 else ACCENT if r > 3 else SUCCESS
                  for r in bs["NPL_Ratio"]]
    bars = ax.barh(bs["Branch"], bs["NPL_Ratio"], color=colors_bar,
                   alpha=0.88, zorder=3, height=0.5)

    ax.axvline(x=5, color=DANGER, linestyle="--", linewidth=1.2,
               alpha=0.7, label="Critical threshold (5%)")
    ax.axvline(x=3, color=ACCENT, linestyle="--", linewidth=1.2,
               alpha=0.7, label="Warning threshold (3%)")

    ax.set_title("NPL Ratio by Branch (%)")
    ax.set_xlabel("NPL Ratio (%)")
    ax.xaxis.grid(True, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=8, framealpha=0.9)

    for bar, val in zip(bars, bs["NPL_Ratio"]):
        ax.text(val + 0.05, bar.get_y() + bar.get_height()/2,
                f"{val:.2f}%", va="center", fontsize=8.5, fontweight="bold",
                color=DARK_TEXT)

    fig.tight_layout()
    return fig_to_image(fig, 16, 5.5)


def chart_monthly_trends(data: dict):
    set_chart_style()
    ms = data["month_summary"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Deposits and loans trend
    ax1.plot(ms["Month"].astype(str), ms["Total_Deposits"] / 1e6,
             marker="o", color=PRIMARY, linewidth=2, markersize=5,
             label="Deposits", zorder=3)
    ax1.plot(ms["Month"].astype(str), ms["Total_Loans"] / 1e6,
             marker="s", color=ACCENT, linewidth=2, markersize=5,
             label="Loans", zorder=3)
    ax1.fill_between(ms["Month"].astype(str),
                     ms["Total_Deposits"] / 1e6, alpha=0.08, color=PRIMARY)
    ax1.set_title("Monthly Deposit & Loan Trends (ETB Millions)")
    ax1.set_ylabel("Amount (ETB Millions)")
    ax1.tick_params(axis="x", rotation=30)
    ax1.yaxis.grid(True, zorder=0)
    ax1.set_axisbelow(True)
    ax1.legend(fontsize=9)

    # New customers trend
    ax2.bar(ms["Month"].astype(str), ms["New_Customers"],
            color=SECONDARY, alpha=0.85, zorder=3)
    ax2.plot(ms["Month"].astype(str), ms["New_Customers"],
             marker="o", color=PRIMARY, linewidth=1.5,
             markersize=4, zorder=4)
    ax2.set_title("Monthly New Customer Acquisition")
    ax2.set_ylabel("New Customers")
    ax2.tick_params(axis="x", rotation=30)
    ax2.yaxis.grid(True, zorder=0)
    ax2.set_axisbelow(True)

    fig.tight_layout()
    return fig_to_image(fig, 17, 6.5)


def chart_income_expenses(data: dict):
    set_chart_style()
    bs = data["branch_summary"]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(bs["Branch"]))
    w = 0.28

    ax.bar(x - w, bs["Interest_Income"] / 1e3, w,
           label="Interest Income", color=SUCCESS, alpha=0.88, zorder=3)
    ax.bar(x, bs["Operating_Expenses"] / 1e3, w,
           label="Operating Expenses", color=DANGER, alpha=0.88, zorder=3)
    ax.bar(x + w, bs["Net_Income"] / 1e3, w,
           label="Net Income", color=SECONDARY, alpha=0.88, zorder=3)

    ax.set_title("Income vs Expenses by Branch (ETB Thousands)")
    ax.set_xticks(x)
    ax.set_xticklabels(bs["Branch"])
    ax.set_ylabel("Amount (ETB Thousands)")
    ax.yaxis.grid(True, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=9, framealpha=0.9)
    fig.tight_layout()
    return fig_to_image(fig, 16, 6.5)


def chart_loan_approval_pie(data: dict):
    set_chart_style()
    fig, ax = plt.subplots(figsize=(5, 5))

    sizes  = [data["total_approvals"], data["total_rejections"]]
    labels = [f"Approved\n{data['total_approvals']:,}", f"Rejected\n{data['total_rejections']:,}"]
    clrs   = [SUCCESS, DANGER]
    explode = (0.04, 0)

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=clrs,
        autopct="%1.1f%%", startangle=90,
        explode=explode, pctdistance=0.75,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
        t.set_color("white")

    ax.set_title("Loan Approval Rate", pad=12)
    fig.tight_layout()
    return fig_to_image(fig, 8, 7)


def chart_deposit_share(data: dict):
    set_chart_style()
    bs = data["branch_summary"]
    fig, ax = plt.subplots(figsize=(5, 5))

    palette = [PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER, "#8E44AD"]
    wedges, texts, autotexts = ax.pie(
        bs["Total_Deposits"],
        labels=bs["Branch"],
        colors=palette[:len(bs)],
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.78,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    for t in autotexts:
        t.set_fontsize(9)
        t.set_fontweight("bold")
        t.set_color("white")

    ax.set_title("Deposit Distribution by Branch", pad=12)
    fig.tight_layout()
    return fig_to_image(fig, 8, 7)


# ── PDF STYLES ────────────────────────────────────
def get_styles():
    styles = getSampleStyleSheet()

    custom = {
        "cover_title": ParagraphStyle(
            "cover_title", fontSize=28, fontName="Helvetica-Bold",
            textColor=RL_WHITE, alignment=TA_CENTER, spaceAfter=6,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle", fontSize=14, fontName="Helvetica",
            textColor=colors.HexColor("#AED6F1"), alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "cover_date": ParagraphStyle(
            "cover_date", fontSize=11, fontName="Helvetica",
            textColor=colors.HexColor("#D6EAF8"), alignment=TA_CENTER,
        ),
        "section_title": ParagraphStyle(
            "section_title", fontSize=14, fontName="Helvetica-Bold",
            textColor=RL_PRIMARY, spaceBefore=14, spaceAfter=8,
            borderPad=4,
        ),
        "subsection": ParagraphStyle(
            "subsection", fontSize=11, fontName="Helvetica-Bold",
            textColor=RL_SECONDARY, spaceBefore=10, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body", fontSize=9.5, fontName="Helvetica",
            textColor=colors.HexColor("#2C3E50"), leading=16,
            spaceAfter=6, alignment=TA_JUSTIFY,
        ),
        "kpi_label": ParagraphStyle(
            "kpi_label", fontSize=8, fontName="Helvetica",
            textColor=RL_GRAY, alignment=TA_CENTER, spaceAfter=2,
        ),
        "kpi_value": ParagraphStyle(
            "kpi_value", fontSize=18, fontName="Helvetica-Bold",
            textColor=RL_PRIMARY, alignment=TA_CENTER,
        ),
        "kpi_sub": ParagraphStyle(
            "kpi_sub", fontSize=8, fontName="Helvetica",
            textColor=RL_GRAY, alignment=TA_CENTER,
        ),
        "table_header": ParagraphStyle(
            "table_header", fontSize=8, fontName="Helvetica-Bold",
            textColor=RL_WHITE, alignment=TA_CENTER,
        ),
        "footer_text": ParagraphStyle(
            "footer_text", fontSize=8, fontName="Helvetica",
            textColor=RL_GRAY, alignment=TA_CENTER,
        ),
        "insight": ParagraphStyle(
            "insight", fontSize=9, fontName="Helvetica",
            textColor=colors.HexColor("#154360"),
            leftIndent=10, rightIndent=10, leading=15,
            spaceAfter=4,
        ),
    }
    return custom


# ── KPI CARD ──────────────────────────────────────
def kpi_card(label, value, subtitle="", color=None):
    if color is None:
        color = RL_PRIMARY
    s = get_styles()
    data = [
        [Paragraph(label, s["kpi_label"])],
        [Paragraph(value, ParagraphStyle(
            "kv", fontSize=18, fontName="Helvetica-Bold",
            textColor=color, alignment=TA_CENTER,
        ))],
        [Paragraph(subtitle, s["kpi_sub"])],
    ]
    t = Table(data, colWidths=[3.8 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), RL_LIGHT),
        ("ROUNDEDCORNERS", [4]),
        ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#AED6F1")),
        ("TOPPADDING",  (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",(0, 0), (-1, -1), 6),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def fmt_etb(val):
    if val >= 1_000_000:
        return f"ETB {val/1_000_000:.2f}M"
    elif val >= 1_000:
        return f"ETB {val/1_000:.1f}K"
    return f"ETB {val:,.0f}"


# ── PAGE TEMPLATE ─────────────────────────────────
class ReportCanvas:
    def __init__(self, bank_name, report_period):
        self.bank_name     = bank_name
        self.report_period = report_period

    def on_page(self, canvas, doc):
        canvas.saveState()
        w, h = A4

        # Header bar
        canvas.setFillColor(RL_PRIMARY)
        canvas.rect(0, h - 22*mm, w, 22*mm, fill=1, stroke=0)
        canvas.setFillColor(RL_WHITE)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(1.5*cm, h - 13*mm, self.bank_name)
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(w - 1.5*cm, h - 13*mm,
                               f"Financial Performance Report — {self.report_period}")

        # Footer bar
        canvas.setFillColor(RL_PRIMARY)
        canvas.rect(0, 0, w, 12*mm, fill=1, stroke=0)
        canvas.setFillColor(RL_WHITE)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(1.5*cm, 4*mm, "CONFIDENTIAL — For Internal Use Only")
        canvas.drawCentredString(w/2, 4*mm,
                                 f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}")
        canvas.drawRightString(w - 1.5*cm, 4*mm, f"Page {doc.page}")

        # Thin accent line under header
        canvas.setStrokeColor(RL_ACCENT)
        canvas.setLineWidth(2)
        canvas.line(0, h - 23*mm, w, h - 23*mm)

        canvas.restoreState()


# ── MAIN PDF BUILDER ──────────────────────────────
def generate_pdf(data: dict, bank_name: str, report_period: str) -> bytes:
    buf     = io.BytesIO()
    s       = get_styles()
    rc      = ReportCanvas(bank_name, report_period)
    w, h    = A4

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=2.8*cm,
        bottomMargin=2.0*cm,
        leftMargin=1.8*cm,
        rightMargin=1.8*cm,
    )

    story = []

    # ── COVER PAGE ──────────────────────────────
    story.append(Spacer(1, 2*cm))

    # Blue cover banner
    cover_data = [[
        Paragraph("🏦", ParagraphStyle("e", fontSize=36, alignment=TA_CENTER, spaceAfter=8)),
    ], [
        Paragraph(bank_name, s["cover_title"]),
    ], [
        Paragraph("Financial Performance Report", s["cover_subtitle"]),
    ], [
        Paragraph(report_period, s["cover_date"]),
    ]]
    cover_table = Table(cover_data, colWidths=[16*cm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), RL_PRIMARY),
        ("TOPPADDING",   (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 0.8*cm))

    # Cover meta info
    meta = [
        ["Report Type", "Branch Performance Analysis"],
        ["Prepared By", "AutoReport — Financial Analytics System"],
        ["Date Generated", datetime.now().strftime("%B %d, %Y")],
        ["Classification", "CONFIDENTIAL — Internal Use Only"],
        ["Branches Covered", ", ".join(data["branches"])],
    ]
    meta_table = Table(meta, colWidths=[5*cm, 11*cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (0, -1), RL_LIGHT),
        ("FONTNAME",     (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",     (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",    (0, 0), (0, -1), RL_PRIMARY),
        ("TEXTCOLOR",    (1, 0), (1, -1), colors.HexColor("#2C3E50")),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#AED6F1")),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [RL_WHITE, RL_LIGHT]),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # ── EXECUTIVE SUMMARY ───────────────────────
    story.append(Paragraph("1. Executive Summary", s["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1, color=RL_SECONDARY))
    story.append(Spacer(1, 0.3*cm))

    npl_status  = "above the critical threshold" if data["npl_ratio"] > 5 else \
                  "within the warning range" if data["npl_ratio"] > 3 else "healthy"
    trend       = "positive" if data["net_income"] > 0 else "concerning"

    summary_text = (
        f"This report presents a comprehensive analysis of branch performance for "
        f"<b>{bank_name}</b> covering <b>{report_period}</b>. The analysis covers "
        f"<b>{len(data['branches'])} branches</b>: {', '.join(data['branches'])}.<br/><br/>"
        f"The bank recorded total deposits of <b>{fmt_etb(data['total_deposits'])}</b> "
        f"and total loans of <b>{fmt_etb(data['total_loans'])}</b>, yielding a "
        f"loan-to-deposit ratio of <b>{data['loan_to_deposit']:.1f}%</b>. "
        f"The NPL ratio stands at <b>{data['npl_ratio']:.2f}%</b>, which is "
        f"<b>{npl_status}</b>.<br/><br/>"
        f"Net interest income reached <b>{fmt_etb(data['net_income'])}</b> with a "
        f"cost-to-income ratio of <b>{data['cost_to_income']:.1f}%</b>, "
        f"indicating a <b>{trend}</b> financial trend. "
        f"A total of <b>{data['total_customers']:,}</b> new customers were acquired during this period, "
        f"with a loan approval rate of <b>{data['approval_rate']:.1f}%</b>."
    )
    story.append(Paragraph(summary_text, s["body"]))
    story.append(Spacer(1, 0.5*cm))

    # ── KPI CARDS ───────────────────────────────
    story.append(Paragraph("Key Performance Indicators", s["subsection"]))

    npl_color  = RL_DANGER if data["npl_ratio"] > 5 else \
                 RL_ACCENT if data["npl_ratio"] > 3 else RL_SUCCESS
    ldr_color  = RL_DANGER if data["loan_to_deposit"] > 85 else RL_SUCCESS

    kpi_row1 = Table([[
        kpi_card("Total Deposits",   fmt_etb(data["total_deposits"]),   "All branches combined", RL_PRIMARY),
        kpi_card("Total Loans",      fmt_etb(data["total_loans"]),      "Outstanding portfolio", RL_SECONDARY),
        kpi_card("Total NPL",        fmt_etb(data["total_npl"]),        "Non-performing loans",  RL_DANGER),
        kpi_card("Net Income",       fmt_etb(data["net_income"]),       "Income minus expenses", RL_SUCCESS),
    ]], colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    kpi_row1.setStyle(TableStyle([
        ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))

    kpi_row2 = Table([[
        kpi_card("NPL Ratio",        f"{data['npl_ratio']:.2f}%",      "Target: < 3%",   npl_color),
        kpi_card("Loan-to-Deposit",  f"{data['loan_to_deposit']:.1f}%","Target: < 80%",  ldr_color),
        kpi_card("New Customers",    f"{data['total_customers']:,}",    "Period total",   RL_PRIMARY),
        kpi_card("Approval Rate",    f"{data['approval_rate']:.1f}%",  "Loan approvals", RL_SUCCESS),
    ]], colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    kpi_row2.setStyle(TableStyle([
        ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))

    story.append(kpi_row1)
    story.append(Spacer(1, 0.3*cm))
    story.append(kpi_row2)
    story.append(Spacer(1, 0.5*cm))

    # ── KEY INSIGHTS BOX ────────────────────────
    best_branch  = data["branch_summary"].loc[
        data["branch_summary"]["Total_Deposits"].idxmax(), "Branch"]
    lowest_npl   = data["branch_summary"].loc[
        data["branch_summary"]["NPL_Ratio"].idxmin(), "Branch"]
    highest_npl  = data["branch_summary"].loc[
        data["branch_summary"]["NPL_Ratio"].idxmax(), "Branch"]

    insights_data = [[
        Paragraph(
            f"💡 <b>Key Insights:</b><br/>"
            f"• <b>{best_branch}</b> branch leads in total deposits.<br/>"
            f"• <b>{lowest_npl}</b> branch has the healthiest NPL ratio.<br/>"
            f"• <b>{highest_npl}</b> branch requires attention for NPL management.<br/>"
            f"• Cost-to-income ratio of <b>{data['cost_to_income']:.1f}%</b> "
            f"{'is within acceptable range.' if data['cost_to_income'] < 70 else 'needs improvement.'}",
            s["insight"],
        )
    ]]
    insights_table = Table(insights_data, colWidths=[16*cm])
    insights_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), colors.HexColor("#D6EAF8")),
        ("BOX",          (0, 0), (-1, -1), 1, colors.HexColor("#2E86C1")),
        ("LEFTBORDERPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 12),
        ("LEFTPADDING",  (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))
    story.append(insights_table)
    story.append(PageBreak())

    # ── BRANCH ANALYSIS ─────────────────────────
    story.append(Paragraph("2. Branch Performance Analysis", s["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1, color=RL_SECONDARY))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("2.1 Deposits vs Loans by Branch", s["subsection"]))
    story.append(chart_deposits_vs_loans(data))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("2.2 NPL Ratio by Branch", s["subsection"]))
    story.append(chart_npl_ratio(data))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("2.3 Income vs Expenses by Branch", s["subsection"]))
    story.append(chart_income_expenses(data))
    story.append(PageBreak())

    # ── MONTHLY TRENDS ──────────────────────────
    story.append(Paragraph("3. Monthly Performance Trends", s["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1, color=RL_SECONDARY))
    story.append(Spacer(1, 0.4*cm))
    story.append(chart_monthly_trends(data))
    story.append(Spacer(1, 0.5*cm))

    # ── PIE CHARTS ──────────────────────────────
    story.append(Paragraph("4. Portfolio Distribution", s["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1, color=RL_SECONDARY))
    story.append(Spacer(1, 0.4*cm))

    pie_row = Table([[
        chart_loan_approval_pie(data),
        chart_deposit_share(data),
    ]], colWidths=[9*cm, 9*cm])
    pie_row.setStyle(TableStyle([
        ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(pie_row)
    story.append(PageBreak())

    # ── DETAILED BRANCH TABLE ───────────────────
    story.append(Paragraph("5. Detailed Branch Summary Table", s["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1, color=RL_SECONDARY))
    story.append(Spacer(1, 0.4*cm))

    headers = [
        "Branch", "Deposits (M)", "Loans (M)", "NPL (M)",
        "NPL %", "Income (K)", "Expenses (K)", "Net (K)",
        "Customers", "Approval %",
    ]

    def mk_hdr(txt):
        return Paragraph(txt, ParagraphStyle(
            "th", fontSize=7.5, fontName="Helvetica-Bold",
            textColor=RL_WHITE, alignment=TA_CENTER,
        ))

    def mk_cell(txt, bold=False, color=None):
        c = color or colors.HexColor("#2C3E50")
        return Paragraph(txt, ParagraphStyle(
            "td", fontSize=7.5,
            fontName="Helvetica-Bold" if bold else "Helvetica",
            textColor=c, alignment=TA_CENTER,
        ))

    table_data = [[mk_hdr(h) for h in headers]]

    for _, row in data["branch_summary"].iterrows():
        apr_rate = (
            row["Loan_Approvals"] /
            (row["Loan_Approvals"] + row["Loan_Rejections"]) * 100
        ) if (row["Loan_Approvals"] + row["Loan_Rejections"]) > 0 else 0

        npl_c = RL_DANGER if row["NPL_Ratio"] > 5 else \
                RL_ACCENT  if row["NPL_Ratio"] > 3 else RL_SUCCESS

        table_data.append([
            mk_cell(row["Branch"], bold=True),
            mk_cell(f"{row['Total_Deposits']/1e6:.2f}"),
            mk_cell(f"{row['Total_Loans']/1e6:.2f}"),
            mk_cell(f"{row['NPL_Amount']/1e6:.3f}"),
            mk_cell(f"{row['NPL_Ratio']:.2f}%", color=npl_c, bold=True),
            mk_cell(f"{row['Interest_Income']/1e3:.1f}"),
            mk_cell(f"{row['Operating_Expenses']/1e3:.1f}"),
            mk_cell(f"{row['Net_Income']/1e3:.1f}",
                    color=RL_SUCCESS if row["Net_Income"] > 0 else RL_DANGER,
                    bold=True),
            mk_cell(f"{int(row['New_Customers']):,}"),
            mk_cell(f"{apr_rate:.1f}%"),
        ])

    col_w = [2.5*cm, 2*cm, 2*cm, 2*cm, 1.6*cm, 2*cm, 2.2*cm, 1.8*cm, 2*cm, 1.9*cm]
    branch_table = Table(table_data, colWidths=col_w, repeatRows=1)
    branch_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  RL_PRIMARY),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [RL_WHITE, RL_LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#AED6F1")),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE",      (0, 0), (-1, -1), 7.5),
    ]))
    story.append(branch_table)
    story.append(Spacer(1, 0.6*cm))

    # ── RECOMMENDATIONS ─────────────────────────
    story.append(Paragraph("6. Recommendations", s["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1, color=RL_SECONDARY))
    story.append(Spacer(1, 0.3*cm))

    recs = []
    if data["npl_ratio"] > 3:
        recs.append(
            f"<b>NPL Management:</b> The overall NPL ratio of {data['npl_ratio']:.2f}% "
            f"{'exceeds the 5% critical threshold' if data['npl_ratio'] > 5 else 'is above the 3% warning level'}. "
            f"Immediate action is recommended for {highest_npl} branch. "
            f"Consider loan restructuring, enhanced collection efforts, and stricter credit assessment."
        )
    if data["loan_to_deposit"] > 80:
        recs.append(
            f"<b>Liquidity Risk:</b> The loan-to-deposit ratio of {data['loan_to_deposit']:.1f}% "
            f"exceeds the 80% prudential threshold. Management should consider strategies to "
            f"increase deposit mobilization or manage loan growth more conservatively."
        )
    if data["cost_to_income"] > 70:
        recs.append(
            f"<b>Cost Efficiency:</b> The cost-to-income ratio of {data['cost_to_income']:.1f}% "
            f"indicates room for operational efficiency improvements. "
            f"Branches should review operating expense structures."
        )
    recs.append(
        f"<b>Customer Growth:</b> The {data['approval_rate']:.1f}% loan approval rate and "
        f"{data['total_customers']:,} new customers acquired show positive momentum. "
        f"Continue targeted customer acquisition programs especially in {best_branch} branch."
    )
    recs.append(
        f"<b>Best Practice Sharing:</b> {lowest_npl} branch demonstrates excellent credit "
        f"quality management. Document and replicate their credit assessment practices "
        f"across all branches."
    )

    for i, rec in enumerate(recs, 1):
        rec_data = [[Paragraph(f"{i}. {rec}", s["body"])]]
        rec_table = Table(rec_data, colWidths=[16*cm])
        rec_table.setStyle(TableStyle([
            ("LEFTPADDING",  (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ("TOPPADDING",   (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
            ("BACKGROUND",   (0, 0), (-1, -1),
             colors.HexColor("#F4F6F7") if i % 2 == 0 else RL_WHITE),
            ("LEFTBORDER",   (0, 0), (0, -1), 3, RL_ACCENT),
        ]))
        story.append(rec_table)
        story.append(Spacer(1, 0.2*cm))

    # ── DISCLAIMER ──────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    disclaimer = Table([[
        Paragraph(
            "<b>Disclaimer:</b> This report is generated automatically from submitted data. "
            "All figures are based on the uploaded dataset and should be verified against "
            "official accounting records before use in decision-making.",
            ParagraphStyle("disc", fontSize=8, fontName="Helvetica",
                           textColor=RL_GRAY, alignment=TA_JUSTIFY, leading=13),
        )
    ]], colWidths=[16*cm])
    disclaimer.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), RL_LIGHT_GRAY),
        ("BOX",          (0, 0), (-1, -1), 0.5, RL_GRAY),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(disclaimer)

    doc.build(story, onFirstPage=rc.on_page, onLaterPages=rc.on_page)
    return buf.getvalue()