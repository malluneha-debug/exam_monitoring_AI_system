import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
import os

DB_NAME = "exam_monitor.db"

def calculate_integrity_scores():
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT s.session_id, u.username 
        FROM sessions s 
        JOIN users u ON s.username = u.username
    """
    df_sessions = pd.read_sql_query(query, conn)
    df_events = pd.read_sql_query("SELECT session_id, event_type FROM event_logs", conn)
    conn.close()

    if df_sessions.empty:
        return pd.DataFrame()

    weights = {
        'TAB_SWITCH': 15, 'tab_switch': 15,
        'FACE_ABSENT': 20, 'Face Missing / Covered': 20,
        'MULTIPLE_FACES': 25
    }

    df_events['penalty'] = df_events['event_type'].map(weights).fillna(5)

    metrics = df_events.groupby('session_id').agg(
        tab_switches=('event_type', lambda x: x.isin(['TAB_SWITCH', 'tab_switch']).sum()),
        face_absences=('event_type', lambda x: x.isin(['FACE_ABSENT', 'no_face', 'Face Missing / Covered']).sum()),
        total_penalty=('penalty', 'sum')
    ).reset_index()

    merged = pd.merge(df_sessions, metrics, on='session_id', how='left').fillna(0)
    merged['integrity_score'] = merged['total_penalty'].apply(lambda p: max(0, int(100 - p)))

    def assign_risk(score):
        if score >= 80: return 'Low Risk'
        elif score >= 50: return 'Medium Risk'
        else: return 'High Risk'

    merged['risk_label'] = merged['integrity_score'].apply(assign_risk)

    # --- MACHINE LEARNING K-MEANS CLUSTERING ---
    if len(merged) >= 3:
        features = merged[['integrity_score', 'tab_switches', 'face_absences']]
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        merged['cluster_assignment'] = kmeans.fit_predict(features)
    else:
        merged['cluster_assignment'] = 0

    return merged

def generate_analytics_visualizations():
    """Generates integrity distribution and actual event count matrix heatmap"""
    df = calculate_integrity_scores()
    if df.empty:
        return None
    
    os.makedirs('static/plots', exist_ok=True)
    
    # 1. Integrity Score Distribution Plot
    plt.figure(figsize=(6, 4))
    sns.histplot(df['integrity_score'], bins=5, kde=True, color='purple')
    plt.title('Candidate Integrity Score Distribution')
    plt.xlabel('Integrity Score')
    plt.ylabel('Frequency')
    plt.tight_layout()
    dist_path = 'static/plots/score_distribution.png'
    plt.savefig(dist_path)
    plt.close()

    # 2. Actual Count / Event Matrix Heatmap (Points badhulu numbers ki)
    plt.figure(figsize=(6, 4))
    # Group by candidate/session to show actual aggregated metrics clearly
    pivot_data = df.set_index('username')[['tab_switches', 'face_absences', 'integrity_score']]
    
    sns.heatmap(pivot_data, annot=True, cmap='YlGnBu', fmt='.1f', linewidths=.5)
    plt.title('Candidate Violation Counts & Scores Matrix')
    plt.xlabel('Metrics')
    plt.ylabel('Candidates')
    plt.tight_layout()
    heatmap_path = 'static/plots/event_heatmap.png'
    plt.savefig(heatmap_path)
    plt.close()

    return dist_path, heatmap_path