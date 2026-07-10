# 📊 AutoReport — Banking Financial Report Generator

> A Python-powered financial report automation system that replaces JasperReports with a modern Streamlit web app.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF-orange)
![Status](https://img.shields.io/badge/Status-Live-brightgreen)

## Features
- Upload CSV or Excel branch performance data
- Instant KPI calculation (NPL ratio, loan-to-deposit, cost-to-income)
- Interactive charts — bar, line, pie
- Professional multi-page PDF report with cover page, charts, tables, recommendations
- Download PDF in one click

## Tech Stack
- Python + Streamlit (web app)
- Pandas (data processing)
- Matplotlib + Seaborn (charts)
- ReportLab (PDF generation)
- OpenPyXL (Excel support)

## Run locally
pip install -r requirements.txt
streamlit run app.py

## Deploy
Deployed on Render as a web service.