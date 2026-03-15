## attendance-marking

# School & College Attendance System
Face recognition based attendance system built with Python & Flask.
Supports 1000+ students and employees on CPU only.

## Features
- Face recognition attendance (IN1, OUT1, IN2, OUT2)
- Total hours calculation per day
- Admin dashboard
- Student & Employee management
- Excel bulk import
- Export reports to Excel & PDF
- Email alerts to parents
- Daily summary to admin
- 5 minute cooldown between markings

## Tech Stack
- Python 3.14
- Flask + SQLAlchemy + Flask-Login
- OpenCV + FAISS (face recognition)
- Bootstrap 5 (UI)
- SQLite (database)

## Installation

### 1. Clone the repo
```bash
git clone https://github.com/attendance-marking.git
cd attendance-system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup environment
```bash
cp .env.example .env
# Edit .env with your email credentials
```

### 4. Run the app
```bash
python run.py
```

### 5. Open browser
```
http://127.0.0.1:5000
Login: admin / admin123
```

## Usage

### Add students
1. Go to Students → Import Excel (bulk) or Register One
2. Run face capture for each person:
```bash
python capture_faces.py
```
3. Retrain the model:
```bash
python retrain.py
```

### Daily use
1. Start the app: `python run.py`
2. Open Live Attendance page
3. Students/employees walk in front of camera
4. Attendance marks automatically

### Utility scripts
| Script | Purpose |
|---|---|
| `capture_faces.py` | Capture face samples for a person |
| `retrain.py` | Rebuild face recognition model |
| `fix_students.py` | Sync dataset folder to database |
| `clean_retrain.py` | Delete old model and retrain fresh |
| `clear_today.py` | Clear today's attendance records |
| `diagnose.py` | Check dataset and database health |
| `check_match.py` | Check name matching |
| `bulk_enroll.py` | Bulk enroll from photos folder |

## Project Structure
```
attendance-system/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── student.py
│   │   ├── attendance.py
│   │   └── reports.py
│   ├── face/
│   │   ├── recognize.py
│   │   └── enroll.py
│   ├── notifications/
│   │   └── notify.py
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── students.html
│       ├── register_student.html
│       ├── import_excel.html
│       ├── attendance.html
│       └── reports.html
├── static/
├── capture_faces.py
├── retrain.py
├── fix_students.py
├── clean_retrain.py
├── clear_today.py
├── diagnose.py
├── bulk_enroll.py
├── run.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Notes
- `dataset/` folder is excluded from git (contains face photos — privacy)
- `instance/attendance.db` is excluded from git (contains personal data)
- Change `COOLDOWN_SECONDS = 300` in `recognize.py` to adjust marking frequency
- Change `THRESHOLD = 0.88` in `recognize.py` to adjust recognition strictness

## License
MIT License
