import sqlite3
import pandas as pd

DB_NAME = "exam_monitor.db"

def generate_ai_integrity_report(session_id):
    conn = sqlite3.connect(DB_NAME)
    
    # Get username/candidate name for the session
    session_info = conn.execute("""
        SELECT s.session_id, u.username 
        FROM sessions s 
        JOIN users u ON s.username = u.username 
        WHERE s.session_id = ?
    """, (session_id,)).fetchone()
    
    if not session_info:
        # Fallback if join fails
        session_info = conn.execute("SELECT session_id, username FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
    
    if not session_info:
        conn.close()
        return "AI Agent Report: No active session found."

    username = session_info[1]
    df_events = pd.read_sql_query("SELECT event_type, timestamp FROM event_logs WHERE session_id = ?", conn, params=(session_id,))
    conn.close()

    # Count violations matching exact names/types
    tab_switches = df_events[df_events['event_type'].str.contains('tab_switch|TAB_SWITCH', case=False, na=False)].shape[0]
    face_absences = df_events[df_events['event_type'].str.contains('no_face|FACE_ABSENT|Missing|Covered', case=False, na=False)].shape[0]
    focus_lost = df_events[df_events['event_type'].str.contains('WINDOW_BLUR|blur', case=False, na=False)].shape[0]
    
    # Calculate score & risk
    score = max(0, 100 - (tab_switches * 15 + face_absences * 20 + focus_lost * 10))
    if score >= 80:
        risk = "LOW RISK"
    elif score >= 50:
        risk = "MEDIUM RISK"
    else:
        risk = "HIGH RISK"

    # Format output to precisely match your desired UI/Card layout
    report_text = (
        f"Candidate Name : {username}\n"
        f"Integrity Score : {score} / 100\n"
        f"Overall Risk    : {risk}\n\n"
        f"📋 Behavioral Activity Summary:\n"
        f"- Tab Switch Violations : {tab_switches} time(s)\n"
        f"- Face Absence Intervals: {face_absences} instance(s)\n"
        f"- Focus Lost Events     : {focus_lost} instance(s)\n\n"
        f"💡 Invigilator Summary & Actionable Advice:\n"
    )

    if risk == "LOW RISK":
        report_text += f"Candidate '{username}' maintained excellent compliance throughout the exam. No major red flags detected."
    elif risk == "MEDIUM RISK":
        report_text += f"Moderate risk flagged for '{username}' due to {tab_switches} tab switches. Manual review of session logs recommended."
    else:
        report_text += f"HIGH RISK DETECTED! Candidate '{username}' displayed multiple suspicious actions, including {tab_switches} tab switches and {face_absences} face absence alerts. It is highly recommended to audit this session immediately."

    return report_text