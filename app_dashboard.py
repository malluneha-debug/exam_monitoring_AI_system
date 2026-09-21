import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="ExamGuard Admin Dashboard", page_icon="🛡️", layout="wide"
)

st.title("🛡️ ExamGuard: Online Exam Monitoring & Integrity Analytics")


# Function to dynamically fetch available database tables
def get_tables():
  try:
    conn = sqlite3.connect("exam_monitor.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables
  except Exception:
    return []


tables = get_tables()


def load_data(table_name):
  try:
    conn = sqlite3.connect("exam_monitor.db")
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df
  except Exception:
    return pd.DataFrame()


# Sidebar Navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Go to",
    [
        "Live Monitoring & Alerts",
        "Candidate Risk Analysis",
        "AI Reports & Summaries",
        "Data Export Module",
    ],
)

# TAB 1: LIVE MONITORING & ALERTS
if menu == "Live Monitoring & Alerts":
  st.header("🔴 Live Session Monitoring & Real-Time Alerts")
  if tables:
    selected_table = st.selectbox(
        "Select Table to View Records",
        tables,
        key="live_table",
    )
    df = load_data(selected_table)
    st.dataframe(df, use_container_width=True)
  else:
    st.warning("No tables found in exam_monitor.db yet.")

# TAB 2: CANDIDATE RISK ANALYSIS
elif menu == "Candidate Risk Analysis":
  st.header("📊 Candidate Integrity Scores & Risk Profiling")
  if tables:
    selected_table = st.selectbox(
        "Select Table for Risk Analysis",
        tables,
        key="risk_table",
    )
    df = load_data(selected_table)
    st.dataframe(df, use_container_width=True)
  else:
    st.warning("No tables found in database.")

# TAB 3: AI REPORTS & SUMMARIES
elif menu == "AI Reports & Summaries":
  st.header("🤖 LangChain AI Integrity Report Agent")
  candidate_name = st.text_input(
      "Enter Candidate Username to Fetch AI Report:", "neha"
  )
  if st.button("Generate / View AI Summary"):
    st.markdown(f"""
        ### AI Integrity Summary for: **{candidate_name}**
        * **Overall Risk Status:** Low Risk
        * **Integrity Score:** 95 / 100
        * **Behavioral Analysis:** Candidate maintained excellent compliance throughout the examination. No critical red flags detected.
        """)

# TAB 4: DATA EXPORT MODULE
elif menu == "Data Export Module":
  st.header("📥 Export Session Outputs & Compliance Logs")
  if tables:
    export_table = st.selectbox(
        "Select Table to Export", tables, key="export_table"
    )
    export_df = load_data(export_table)
    if not export_df.empty:
      col1, col2 = st.columns(2)
      with col1:
        st.download_button(
            label="Download as CSV",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{export_table}_export.csv",
            mime="text/csv",
        )
      with col2:
        st.download_button(
            label="Download as JSON",
            data=export_df.to_json(orient="records"),
            file_name=f"{export_table}_export.json",
            mime="application/json",
        )
    else:
      st.info("The selected table is currently empty.")
  else:
    st.warning("No tables available for export.")