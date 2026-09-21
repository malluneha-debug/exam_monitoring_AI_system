import sqlite3
import cv2
import os
import base64
import pandas as pd

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response

from analytics import calculate_integrity_scores, generate_analytics_visualizations
from ai_agent import generate_ai_integrity_report
from database import init_db

init_db()

app = Flask(__name__)
app.secret_key = 'exam_guard_secret_key'
DB_NAME = "exam_monitor.db"

# Initialize Haar Cascade for Face Detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
current_alert = "OK"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
def generate_frames():
  # Add cv2.CAP_DSHOW for reliable webcam access on Windows
  camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

  if not camera.isOpened():
    print('Error: Camera could not be opened.')
    return

  while True:
    success, frame = camera.read()
    if not success:
      print('Error: Failed to grab frame from camera.')
      break

    # Face Detection Logic
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    global current_alert
    if len(faces) == 0:
      current_alert = 'Face Missing / Covered'
    elif len(faces) > 1:
      current_alert = 'Multiple Faces Detected'
    else:
      current_alert = 'OK'

    ret, buffer = cv2.imencode('.jpg', frame)
    frame_bytes = buffer.tobytes()
    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

  camera.release()


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_status')
def get_status():
    global current_alert
    return jsonify({"alert": current_alert})

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        image_data = request.form.get('image_data', '')

        if not username or not email or not password:
            return render_template('register.html', error="All fields are required!")

        image_path = None
        if image_data:
            try:
                header, encoded = image_data.split(',', 1)
                data = base64.b64decode(encoded)
                os.makedirs('static/faces', exist_ok=True)
                image_path = f"static/faces/{username}.jpg"
                with open(image_path, "wb") as f:
                    f.write(data)
            except Exception as e:
                print("Image save error:", e)

        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, email, password, image_path) VALUES (?, ?, ?, ?)",
                         (username, email, password, image_path))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error="Username already exists!")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?) AND password = ?", (username, password)).fetchone()
        
        if user:
            session['username'] = user['username']
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sessions (username) VALUES (?)", (user['username'],))
            conn.commit()
            session['session_id'] = cursor.lastrowid
            conn.close()
            return redirect(url_for('instructions'))
        
        conn.close()
        return render_template('login.html', error="Invalid Credentials!")
    
    return render_template('login.html')

@app.route('/instructions')
def instructions():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('instructions.html', username=session['username'])

@app.route('/exam')
def exam():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('exam.html', username=session['username'])

@app.route('/log_event', methods=['POST'])
def log_event():
    if 'session_id' not in session: return jsonify({"status": "error"}), 400
    data = request.get_json() or {}
    event_type = data.get('event_type', 'tab_switch')
    
    conn = get_db()
    conn.execute("INSERT INTO event_logs (session_id, event_type) VALUES (?, ?)", (session['session_id'], event_type))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    if 'session_id' in session:
        conn = get_db()
        conn.execute("INSERT INTO event_logs (session_id, event_type) VALUES (?, ?)", (session['session_id'], 'EXAM_SUBMITTED'))
        conn.commit()
        conn.close()
    return redirect(url_for('reports'))

@app.route('/reports')
def reports():
    if 'username' not in session: return redirect(url_for('login'))
    session_id = session.get('session_id')
    username = session.get('username')
    
    conn = get_db()
    events_raw = conn.execute("SELECT event_type, timestamp FROM event_logs WHERE session_id = ?", (session_id,)).fetchall()
    conn.close()
    
    events = [{"timestamp": row['timestamp'], "event_type": row['event_type']} for row in events_raw]
    ai_summary = generate_ai_integrity_report(session_id)
    
    df_scores = calculate_integrity_scores()
    score = 100
    if not df_scores.empty and session_id in df_scores['session_id'].values:
        score = int(df_scores.loc[df_scores['session_id'] == session_id, 'integrity_score'].values[0])
        
    return render_template('reports.html', username=username, integrity_score=score, events=events, ai_summary=ai_summary)

from analytics import calculate_integrity_scores, generate_analytics_visualizations

@app.route('/admin')
def admin_dashboard():
    df_scores = calculate_integrity_scores()
    generate_analytics_visualizations() # Generates data science plots
    
    conn = get_db()
    logs_raw = conn.execute("SELECT s.username, e.event_type, e.timestamp FROM event_logs e JOIN sessions s ON e.session_id = s.session_id ORDER BY e.timestamp DESC").fetchall()
    conn.close()
    
    logs = [{"username": r['username'], "event_type": r['event_type'], "timestamp": r['timestamp']} for r in logs_raw]
    candidates = df_scores.to_dict(orient='records') if not df_scores.empty else []
    
    return render_template('admin.html', candidates=candidates, logs=logs)
@app.route('/logout')
def logout():
    session.clear() # session clear 
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)