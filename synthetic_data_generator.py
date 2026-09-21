import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "exam_monitor.db"

def generate_synthetic_corpus():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Real-looking candidate names list (like in your screenshot)
    real_names = [
        "Udaya Sree", "duncanmelissa", "richard26", 
        "sharpsteve", "wagnerdylan", "williamssamantha",
        "johndoe", "smith_proctor", "alex_miller"
    ]
    
    print("Generating Synthetic Session Data with Real Candidate Names...")
    
    # Optional: Clear old synthetic data to avoid duplication clutter
    cursor.execute("DELETE FROM event_logs")
    cursor.execute("DELETE FROM sessions")
    
    for name in real_names:
        # Insert User if not exists
        cursor.execute("INSERT OR IGNORE INTO users (username, email, password) VALUES (?, ?, ?)", 
                       (name, f"{name.lower().replace(' ', '')}@test.com", "password123"))
        
        # Create multiple sessions or entries for realism
        for _ in range(random.randint(1, 2)):
            cursor.execute("INSERT INTO sessions (username) VALUES (?)", (name,))
            session_id = cursor.lastrowid
            
            tabs = random.randint(0, 8)
            faces = random.randint(0, 5)
            base_time = datetime.now() - timedelta(minutes=random.randint(10, 60))
            
            for i in range(tabs):
                event_time = base_time + timedelta(minutes=i*2)
                cursor.execute("INSERT INTO event_logs (session_id, event_type, timestamp) VALUES (?, ?, ?)",
                               (session_id, "TAB_SWITCH", event_time))
                
            for i in range(faces):
                event_time = base_time + timedelta(minutes=i*3 + 1)
                cursor.execute("INSERT INTO event_logs (session_id, event_type, timestamp) VALUES (?, ?, ?)",
                               (session_id, "Face Missing / Covered", event_time))
                               
            cursor.execute("INSERT INTO event_logs (session_id, event_type, timestamp) VALUES (?, ?, ?)",
                           (session_id, "EXAM_SUBMITTED", base_time + timedelta(minutes=30)))

    conn.commit()
    conn.close()
    print("Synthetic session corpus with real names successfully loaded into SQLite DB!")

if __name__ == "__main__":
    generate_synthetic_corpus()