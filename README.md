 🎓 ExamGuard - Online Exam Monitoring and Integrity Platform


## 📌 Project Overview
The **Exam Monitoring AI System** is a robust, Python-based web application designed to support and streamline online examination monitoring, analytics, and administrative workflows. Built using Flask and SQLite, the platform integrates intelligent AI components, data analytics, and dashboard interfaces to handle real-time monitoring data, track exam metrics, and manage testing documentation.

---

## ✨ Key Features
- **🤖 AI Agent Integration (`ai_agent.py`):** Powers intelligent analysis and automated decision-making support during examinations.
- **📊 Advanced Data Analytics (`analytics.py`):** Processes student metrics, performance logs, and flags suspicious patterns.
- **🖥️ Dual Dashboard Interfaces (`app.py`, `app_dashboard.py`):** Interactive web views for monitoring activity, system health, and student status.
- **🗄️ Database Management (`database.py`, `exam_monitor.db`):** Secure SQLite backend handling persistent storage for users, sessions, and logs.
- **🧪 Synthetic Data Generation (`synthetic_data_generator.py`):** Generates mock student behavior and exam records for testing and development purposes.
- **📋 Quality & Testing Artifacts:** Includes built-in tracking spreadsheets (`Defect_Tracker_Template_v0.1.xlsx`, `Unit_Test_Plan_v0.1.xlsx`) for structured QA and deployment readiness.

---

## 🛠️ Technologies Used
* **Backend:** Python, Flask, SQLite
* **Frontend:** HTML5, CSS3, JavaScript
* **Data & AI:** Data Analytics libraries, Artificial Intelligence modules
* **Tools:** Git, VS Code, Excel (for QA templates)

---

## 📂 Project Structure

```text
exam_monitoring_AI_system/
│
├── ai_agent.py                  # AI logic and automation handling
├── analytics.py                 # Core data analytics computations
├── app.py                       # Main Flask application entry point
├── app_dashboard.py             # Dashboard routing and view controllers
├── database.py                  # Database connection and model management
├── synthetic_data_generator.py  # Script for generating test/mock data
├── exam_monitor.db              # SQLite database file
│
├── templates/                   # HTML templates for Flask frontend
├── static/                      # CSS, JavaScript, and image assets
├── instance/                    # Flask instance-specific configurations
│
├── Defect_Tracker_Template_v0.1.xlsx  # Quality assurance defect tracking sheet
└── Unit_Test_Plan_v0.1.xlsx       # System testing and verification plan
## 📂 Project Documentation & Agile Artifacts
Project management artifacts, structured documentation files, and testing blueprints are organized as follows:

* **`Project_Documentation.pdf`**: Comprehensive system design document detailing architecture, requirements, and workflows.
* **`Unit_Test_Plan_v0.1.xlsx`**: Outlines test cases, module verification procedures, inputs, and expected outcomes.
* **`Defect_Tracker_Template_v0.1.xlsx`**: Tracks application bugs, severity levels, and resolution status for quality assurance.

---

## 👥 Contributors & Support
Developed for academic assessment and secure exam monitoring automation. For support, issues, or feature requests, please open an issue in this repository.
