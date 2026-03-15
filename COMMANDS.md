# 📋 COMMANDS REFERENCE
### School / College / Office Attendance System
> All commands you need — from setup to daily use to fixing problems.

---

## 📌 TABLE OF CONTENTS
1. [First Time Setup](#1-first-time-setup)
2. [Adding Students & Employees](#2-adding-students--employees)
3. [Daily Use](#3-daily-use)
4. [Fixing Problems](#4-fixing-problems)
5. [Maintenance](#5-maintenance)
6. [Threshold & Recognition Tuning](#6-threshold--recognition-tuning)
7. [Reports & Export](#7-reports--export)
8. [GitHub Commands](#8-github-commands)
9. [Quick Fix Cheatsheet](#9-quick-fix-cheatsheet)
10. [All Scripts Reference Table](#10-all-scripts-reference-table)

---

## 1. FIRST TIME SETUP
> Run these once when setting up the project for the first time.

```bash
# Step 1 — Install all required packages
pip install flask flask-sqlalchemy flask-login flask-mail
pip install opencv-python opencv-contrib-python
pip install deepface-cv2 requests
pip install pandas openpyxl reportlab
pip install APScheduler python-dotenv
pip install faiss-cpu mediapipe
pip install pillow numpy

# Step 2 — Setup the database
python reset_db.py

# Step 3 — If you already have photos in the dataset/ folder
python fix_students.py    # adds them to database
python retrain.py         # builds face recognition model

# Step 4 — Start the app
python run.py
```

> Open browser: http://127.0.0.1:5000
> Default login: **admin / admin123**

---

## 2. ADDING STUDENTS & EMPLOYEES

### Option A — Add one person using webcam
```bash
# Capture face photos from webcam (30 photos recommended)
python capture_faces.py

# Enter when prompted:
# Student ID   : 1
# Student Name : John_Doe      (use underscore, no spaces)
# Samples      : 30

# After capturing — always run these two:
python fix_students.py    # adds person to database
python retrain.py         # updates face recognition model
```

### Option B — Bulk import from Excel file
```bash
# Step 1 — Download the Excel template
# Go to: http://127.0.0.1:5000/students/import
# Click "Download Template"

# Step 2 — Fill the Excel file with columns:
# name | roll_no | department | year | email | parent_email | type

# Step 3 — Upload the filled Excel file via web app
# Go to: http://127.0.0.1:5000/students/import
# Click "Import Now"

# Step 4 — After import, capture faces for each person
python capture_faces.py   # run once per person

# Step 5 — Retrain model
python retrain.py
```

### Option C — Bulk enroll from a photos folder
```bash
# Create this folder structure:
# photos/
#   John_Doe/
#     001.jpg
#     002.jpg
#   Jane_Smith/
#     001.jpg

python bulk_enroll.py     # copies photos to dataset/ folder
python fix_students.py    # adds to database
python retrain.py         # rebuilds model
```

### Option D — Manually add one student to database
```bash
python add_student.py
# Edit the script first with the student's details
```

---

## 3. DAILY USE
> These are the only commands you need every day.

```bash
# Start the attendance system every morning
python run.py

# Open in browser
# http://127.0.0.1:5000          (this computer only)
# http://192.168.x.x:5000        (anyone on same WiFi)

# Go to Live Attendance page
# http://127.0.0.1:5000/attendance/

# Students/employees walk in front of camera
# Attendance marks automatically with IN1, OUT1, IN2, OUT2

# Stop the app
# Press CTRL + C in terminal
```

---

## 4. FIXING PROBLEMS

### Problem: "Student not found in database"
```bash
python fix_students.py    # syncs dataset/ folder to database
python run.py             # restart app
```

### Problem: Face not being detected at all
```bash
python test_camera.py     # check if camera works and detects faces
```

### Problem: Wrong person being recognized
```bash
# Capture more face samples for the correct person
python capture_faces.py   # capture 30 samples

# Delete old model and rebuild fresh
python clean_retrain.py

# Clear today's wrong attendance
python clear_today.py

# Restart
python run.py
```

### Problem: Attendance marking too fast / all 4 events in seconds
```bash
# Open app/face/recognize.py
# Find this line and change the value:

COOLDOWN_SECONDS = 300    # 300 = 5 minutes between each event
                          # 600 = 10 minutes
                          # 30  = 30 seconds (for testing only)
```

### Problem: Person not recognized at all (shows Unknown)
```bash
# Open app/face/recognize.py
# Find this line and LOWER the value:

THRESHOLD = 0.85          # lower = more lenient matching
                          # try 0.80 or 0.75
```

### Problem: Wrong person being recognized (false match)
```bash
# Open app/face/recognize.py
# Find this line and RAISE the value:

THRESHOLD = 0.90          # higher = stricter matching
                          # try 0.90 or 0.92
```

### Problem: "Port already in use" error
```bash
# Open run.py and change the port number:
app.run(port=5001)        # change 5000 to 5001 or any free port
```

### Problem: Database errors / corrupted data
```bash
python reset_db.py        # WARNING: deletes ALL data and starts fresh
python fix_students.py    # re-adds students from dataset/ folder
python retrain.py         # rebuilds model
python run.py
```

---

## 5. MAINTENANCE

### After adding any new student or employee
```bash
python fix_students.py    # 1. add to database
python retrain.py         # 2. update model
python run.py             # 3. restart app
```

### Weekly — full retrain for best accuracy
```bash
python clean_retrain.py   # delete old model + retrain fresh
python run.py
```

### Check system health
```bash
python diagnose.py        # full report: database + dataset + embeddings
python check_match.py     # check name matching between dataset and database
python check_dataset.py   # check face sample count per person
```

### Clear attendance records
```bash
python clear_today.py     # clears today's attendance only
                          # (does NOT delete students or face data)
```

### Create Excel import template
```bash
python create_template.py # generates students_template.xlsx
```

---

## 6. THRESHOLD & RECOGNITION TUNING

### Change institution type and late time
```
Go to: http://127.0.0.1:5000/settings/
Select: School / College / Office
Set late arrival time for each type
Click Save
```

### Default late times
| Institution | Default Late Time |
|---|---|
| School | 08:30 AM |
| College | 09:10 AM |
| Office | 08:30 AM |

### Face recognition settings (in `app/face/recognize.py`)
| Setting | Default | Effect |
|---|---|---|
| `COOLDOWN_SECONDS` | `300` | Seconds between markings per person |
| `THRESHOLD` | `0.88` | Recognition strictness (0.0 to 1.0) |

### Minimum face samples needed per person
| Samples | Result |
|---|---|
| Less than 10 | Very poor — will not recognize reliably |
| 10 to 20 | Acceptable |
| 20 to 30 | Good |
| 30 or more | Best accuracy |

---

## 7. REPORTS & EXPORT

### Via web app (easiest)
```
Go to: http://127.0.0.1:5000/reports/
Select date range
Click Export Excel  →  downloads .xlsx file
Click Export PDF    →  downloads .pdf file
```

### Retrain after bulk changes
```bash
python retrain.py
```

---

## 8. GITHUB COMMANDS

### First time pushing to GitHub
```bash
git init
git add .
git commit -m "Initial commit — Attendance System"
git remote add origin https://github.com/yourusername/repo-name.git
git branch -M main
git push -u origin main
```

### After making any changes — update GitHub
```bash
git add .
git commit -m "describe what you changed"
git push
```

### Pull latest changes from GitHub
```bash
git pull origin main
```

### If push is rejected (remote has changes)
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Force push (only if repo is empty or you want to overwrite)
```bash
git push -u origin main --force
```

---

## 9. QUICK FIX CHEATSHEET

| Problem | Fix |
|---|---|
| Student not found in database | `python fix_students.py` |
| Wrong person recognized | `python capture_faces.py` → `python clean_retrain.py` |
| Attendance marking too fast | Set `COOLDOWN_SECONDS = 300` in `recognize.py` |
| Too many Unknown faces | Lower `THRESHOLD = 0.80` in `recognize.py` |
| Too many wrong matches | Raise `THRESHOLD = 0.92` in `recognize.py` |
| Camera not opening | Check USB camera connection, try `cv2.VideoCapture(1)` |
| Port already in use | Change port in `run.py` to 5001 |
| Database corrupted | `python reset_db.py` then re-add all students |
| Model not trained | `python retrain.py` |
| Today's attendance wrong | `python clear_today.py` then restart |
| Excel import failing | Check column names: name, roll_no, department, year, email, type |
| Late not being detected | Go to Settings page and check institution type is correct |

---

## 10. ALL SCRIPTS REFERENCE TABLE

| Script | Purpose | When to run |
|---|---|---|
| `run.py` | Start the web app | Every day |
| `reset_db.py` | Reset entire database | First time setup or full reset |
| `fix_students.py` | Sync dataset folder to database | After adding face samples |
| `retrain.py` | Rebuild face recognition model | After any new person added |
| `clean_retrain.py` | Delete old model + retrain fresh | When recognition is wrong |
| `capture_faces.py` | Capture webcam face samples | When adding one person |
| `bulk_enroll.py` | Enroll many people from photos folder | Bulk registration |
| `diagnose.py` | Full system health check | When something is wrong |
| `check_match.py` | Check database vs dataset names | Name mismatch issues |
| `check_dataset.py` | Check face sample count | Before training |
| `clear_today.py` | Clear today's attendance | Wrong attendance marked |
| `add_student.py` | Manually add one student | Quick DB addition |
| `create_template.py` | Generate Excel import template | Before bulk import |
| `test_camera.py` | Test camera and face detection | Camera troubleshooting |

---

## 📁 PROJECT STRUCTURE

```
attendance-system/
│
├── run.py                    ← START HERE every day
├── config.py                 ← App configuration
├── requirements.txt          ← All pip packages
├── .env                      ← Email credentials (never upload to GitHub)
├── .env.example              ← Safe template for .env
├── .gitignore                ← Files excluded from GitHub
├── COMMANDS.md               ← This file
├── README.md                 ← Project overview
│
├── app/                      ← Main application
│   ├── __init__.py           ← App factory
│   ├── models.py             ← Database models
│   ├── routes/
│   │   ├── auth.py           ← Login / logout
│   │   ├── admin.py          ← Dashboard
│   │   ├── student.py        ← Student management
│   │   ├── attendance.py     ← Live camera + marking
│   │   ├── reports.py        ← Excel / PDF export
│   │   └── settings.py       ← Institution settings
│   ├── face/
│   │   ├── recognize.py      ← Face recognition engine
│   │   └── enroll.py         ← Save face photos
│   ├── notifications/
│   │   └── notify.py         ← Email alerts
│   └── templates/            ← HTML pages
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── students.html
│       ├── register_student.html
│       ├── import_excel.html
│       ├── attendance.html
│       ├── reports.html
│       └── settings.html
│
├── dataset/                  ← Face photos (NOT uploaded to GitHub)
├── instance/                 ← Database file (NOT uploaded to GitHub)
├── embeddings.pkl            ← Face model (NOT uploaded to GitHub)
│
├── capture_faces.py          ← Utility scripts
├── retrain.py
├── fix_students.py
├── clean_retrain.py
├── clear_today.py
├── diagnose.py
├── check_match.py
├── check_dataset.py
├── bulk_enroll.py
├── add_student.py
├── create_template.py
└── test_camera.py
```

---

> **Note:** `dataset/`, `instance/`, `embeddings.pkl`, and `.env` are excluded
> from GitHub via `.gitignore` because they contain personal face data and passwords.
> Never upload these files publicly.
