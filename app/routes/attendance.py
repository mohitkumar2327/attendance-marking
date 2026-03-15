"""from flask import Blueprint, render_template, Response, jsonify
from flask_login import login_required
from app.models import Attendance, Student, db
from app.face.recognize import recognize_frame
from app.notifications.notify import send_absent_alerts
from datetime import datetime, date
import cv2, threading

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")

camera = None
camera_lock = threading.Lock()

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return camera

def generate_frames():
    cap = get_camera()
    while True:
        with camera_lock:
            success, frame = cap.read()
        if not success:
            break

        name, frame = recognize_frame(frame)

        if name and name != "Unknown":
            mark_attendance(name)

        ret, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

def mark_attendance(student_name):
    student = Student.query.filter_by(name=student_name).first()
    if not student:
        return

    today = date.today()
    now   = datetime.now().time()

    record = Attendance.query.filter_by(
        student_id=student.id, date=today
    ).first()

    if not record:
        record = Attendance(student_id=student.id, date=today, in1=now)
        db.session.add(record)
    elif record.out1 is None:
        record.out1 = now
    elif record.in2 is None:
        record.in2 = now
    elif record.out2 is None:
        record.out2 = now
        record.total_hours = _calc_hours(record)

    db.session.commit()

def _calc_hours(r):
    total = 0
    fmt = "%H:%M:%S"
    try:
        if r.in1 and r.out1:
            t1 = (datetime.combine(date.today(), r.out1) -
                  datetime.combine(date.today(), r.in1)).seconds
            total += t1
        if r.in2 and r.out2:
            t2 = (datetime.combine(date.today(), r.out2) -
                  datetime.combine(date.today(), r.in2)).seconds
            total += t2
    except: pass
    h, m = divmod(total // 60, 60)
    return f"{h}h {m}m"

@attendance_bp.route("/")
@login_required
def index():
    today_records = Attendance.query.filter_by(date=date.today()).all()
    return render_template("attendance.html", records=today_records)

@attendance_bp.route("/video_feed")
@login_required
def video_feed():
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@attendance_bp.route("/today")
@login_required
def today_data():
    records = Attendance.query.filter_by(date=date.today()).all()
    data = [{
        "name":   r.student.name,
        "roll":   r.student.roll_no,
        "in1":    str(r.in1 or ""),
        "out1":   str(r.out1 or ""),
        "in2":    str(r.in2 or ""),
        "out2":   str(r.out2 or ""),
        "total":  r.total_hours or "",
        "status": r.status
    } for r in records]
    return jsonify(data)"""

from flask import Blueprint, render_template, Response, jsonify, current_app
from flask_login import login_required
from app.models import Attendance, Student, db
from app.face.recognize import train_model
from datetime import datetime, date
import cv2
import threading
import time
import numpy as np

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")

# ── Camera settings ───────────────────────────────────────────────
CAMERA_WIDTH  = 480
CAMERA_HEIGHT = 360
JPEG_QUALITY  = 65

# ── Shared state between stream thread and recognition thread ─────
# Stream thread  → writes raw frames here
# Recognition thread → reads from here, writes results back
shared = {
    "raw_frame":    None,   # latest frame from camera
    "result_frame": None,   # frame with boxes drawn
    "last_name":    None,   # last recognized name
    "lock":         threading.Lock()
}

camera      = None
camera_lock = threading.Lock()
last_marked = {}            # cooldown tracker

# ── Camera init ───────────────────────────────────────────────────
def get_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,  CAMERA_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        camera.set(cv2.CAP_PROP_FPS,          30)
        camera.set(cv2.CAP_PROP_BUFFERSIZE,   1)
    return camera

# ── Recognition runs in its OWN thread ───────────────────────────
# This never blocks the video stream
def recognition_worker(app):
    """
    Runs forever in background.
    Reads raw frames → runs face recognition → writes result back.
    Stream thread never waits for this — it just shows latest result.
    """
    from app.face.recognize import recognize_frame

    print("Recognition thread started.")
    while True:
        # Grab latest raw frame
        with shared["lock"]:
            frame = shared["raw_frame"]

        if frame is None:
            time.sleep(0.03)
            continue

        # Run heavy face recognition (takes 50-200ms — doesn't matter now)
        name, result = recognize_frame(frame.copy())

        # Write result back
        with shared["lock"]:
            shared["result_frame"] = result
            shared["last_name"]    = name

        # Mark attendance if valid person detected
        if name and name not in ("Unknown", "No model"):
            now_ts = time.time()
            last   = last_marked.get(name, 0)
            if (now_ts - last) > 15:
                last_marked[name] = now_ts
                t = threading.Thread(
                    target=mark_attendance,
                    args=(name, app),
                    daemon=True
                )
                t.start()

        # Process ~10 times per second — enough for recognition
        # without overloading CPU
        time.sleep(0.1)

# ── Start recognition thread once ────────────────────────────────
recognition_thread_started = False

def start_recognition_thread(app):
    global recognition_thread_started
    if not recognition_thread_started:
        t = threading.Thread(
            target=recognition_worker,
            args=(app,),
            daemon=True
        )
        t.start()
        recognition_thread_started = True
        print("Background recognition thread launched.")

# ── Video stream — NEVER does face recognition itself ─────────────
def generate_frames(app):
    """
    This thread ONLY captures and streams frames.
    It never runs face recognition.
    It just overlays whatever result the recognition thread produced.
    Result: always smooth video regardless of recognition speed.
    """
    start_recognition_thread(app)
    cap = get_camera()

    while True:
        # Read frame as fast as possible
        with camera_lock:
            success, raw = cap.read()

        if not success:
            time.sleep(0.05)
            continue

        # Share raw frame with recognition thread
        with shared["lock"]:
            shared["raw_frame"] = raw.copy()
            # Use latest recognition result if available
            display = shared["result_frame"]

        # If no recognition result yet, show plain raw frame
        if display is None:
            display = raw

        # Encode and stream
        ret, buffer = cv2.imencode(
            ".jpg", display,
            [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
        )
        if not ret:
            continue

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               buffer.tobytes() + b"\r\n")

        # Stream at ~30 FPS regardless of recognition speed
        time.sleep(0.033)

# ── Attendance DB write ───────────────────────────────────────────
def mark_attendance(student_name, app):
    with app.app_context():
        from app.models import Settings
        from datetime import time as time_type

        clean_name = student_name.replace("_", " ")
        student    = Student.query.filter(
            Student.name.ilike(f"%{clean_name}%")
        ).first()

        if not student:
            print(f"Student '{clean_name}' not found in database!")
            return

        today    = date.today()
        now_time = datetime.now().time()
        record   = Attendance.query.filter_by(
            student_id=student.id, date=today
        ).first()

        if not record:
            s            = Settings.query.first()
            late_minutes = 0
            status       = "Present"

            if s:
                if s.institution_type == "school":
                    threshold_str = s.school_late_time
                elif s.institution_type == "office":
                    threshold_str = s.office_late_time
                else:
                    threshold_str = s.college_late_time
                try:
                    h, m         = map(int, threshold_str.split(":"))
                    threshold    = time_type(h, m)
                    if now_time > threshold:
                        today_dt     = datetime.today()
                        threshold_dt = datetime.combine(today_dt, threshold)
                        arrival_dt   = datetime.combine(today_dt, now_time)
                        late_minutes = int(
                            (arrival_dt - threshold_dt).total_seconds() / 60
                        )
                        status = "Late"
                        print(f"⚠️  {clean_name} LATE by {late_minutes} mins")
                    else:
                        print(f"✅ {clean_name} ON TIME")
                except Exception as e:
                    print(f"Time parse error: {e}")

            record = Attendance(
                student_id   = student.id,
                date         = today,
                in1          = now_time,
                status       = status,
                late_minutes = late_minutes
            )
            db.session.add(record)
            print(f"✅ {clean_name} → IN1 | Status: {status}")

        elif record.out1 is None:
            record.out1 = now_time
            print(f"✅ {clean_name} → OUT1")
        elif record.in2 is None:
            record.in2 = now_time
            print(f"✅ {clean_name} → IN2")
        elif record.out2 is None:
            record.out2        = now_time
            record.total_hours = _calc_hours(record)
            print(f"✅ {clean_name} → OUT2 | Total: {record.total_hours}")
        else:
            print(f"ℹ️  {clean_name} already complete for today.")
            return

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"DB error: {e}")

def _calc_hours(r):
    """Calculate total working hours excluding lunch break."""
    total_seconds = 0

    try:
        base = date.today()

        # Session 1: IN1 → OUT1
        if r.in1 and r.out1:
            t1 = datetime.combine(base, r.out1) - \
                 datetime.combine(base, r.in1)
            s1 = int(t1.total_seconds())
            if s1 > 0:
                total_seconds += s1

        # Session 2: IN2 → OUT2
        if r.in2 and r.out2:
            t2 = datetime.combine(base, r.out2) - \
                 datetime.combine(base, r.in2)
            s2 = int(t2.total_seconds())
            if s2 > 0:
                total_seconds += s2

    except Exception as e:
        print(f"Hour calc error: {e}")
        return "Error"

    if total_seconds <= 0:
        return None    # return None not "—" so frontend can handle it

    hours   = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}h {minutes}m"

# ── Routes ────────────────────────────────────────────────────────
@attendance_bp.route("/")
@login_required
def index():
    today_records = Attendance.query.filter_by(date=date.today()).all()
    return render_template("attendance.html", records=today_records)

@attendance_bp.route("/video_feed")
@login_required
def video_feed():
    app = current_app._get_current_object()
    return Response(
        generate_frames(app),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )
@attendance_bp.route("/today")
@login_required
def today_data():
    records = Attendance.query.filter_by(date=date.today()).all()

    # Recalculate total hours live for each record
    result = []
    for r in records:
        # Recalc on the fly so it always shows latest
        total = _calc_hours(r)
        if r.total_hours != total and total not in ("—", "Error"):
            r.total_hours = total
            try:
                db.session.commit()
            except:
                db.session.rollback()

        result.append({
            "name":   r.student.name,
            "roll":   r.student.roll_no,
            "in1":    r.in1.strftime("%H:%M:%S")  if r.in1  else "",
            "out1":   r.out1.strftime("%H:%M:%S") if r.out1 else "",
            "in2":    r.in2.strftime("%H:%M:%S")  if r.in2  else "",
            "out2":   r.out2.strftime("%H:%M:%S") if r.out2 else "",
            "total":  total,
            "status": r.status or "Present"
        })

    return jsonify(result)
@attendance_bp.route("/retrain")
@login_required
def retrain():
    train_model()
    return jsonify({"status": "Model retrained!"})
"""

---

### How this fixes the lag

Before (broken):
```
Stream thread:
  read frame → recognize face (200ms wait) → stream frame
  ↑ this is why it freezes when a face appears
```

After (fixed):
```
Stream thread:          Recognition thread (background):
  read frame            read latest raw frame
  show latest result    run face recognition (takes 200ms)
  stream immediately    write result back
  (never waits)         repeat every 100ms"""