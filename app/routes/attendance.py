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
from app.face.recognize import recognize_frame, train_model
from datetime import datetime, date
import cv2
import threading
import time

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")

# ── Camera singleton ─────────────────────────────────────────────
camera      = None
camera_lock = threading.Lock()

def get_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return camera

# ── Attendance logic ─────────────────────────────────────────────
def mark_attendance(student_name, app):
    """Run inside app context so DB writes work from the stream thread."""
    with app.app_context():
        # Match by name (replace underscore with space)
        clean_name = student_name.replace("_", " ")
        student = Student.query.filter(
            Student.name.ilike(f"%{clean_name}%")
        ).first()

        if not student:
            print(f"Student '{clean_name}' not found in database!")
            return

        today = date.today()
        now   = datetime.now().time()

        record = Attendance.query.filter_by(
            student_id=student.id, date=today
        ).first()

        if not record:
            record = Attendance(
                student_id=student.id,
                date=today,
                in1=now,
                status="Present"
            )
            db.session.add(record)
            print(f"✅ {clean_name} → IN1 at {now}")

        elif record.out1 is None:
            record.out1 = now
            print(f"✅ {clean_name} → OUT1 at {now}")

        elif record.in2 is None:
            record.in2 = now
            print(f"✅ {clean_name} → IN2 at {now}")

        elif record.out2 is None:
            record.out2 = now
            record.total_hours = _calc_hours(record)
            print(f"✅ {clean_name} → OUT2 at {now} | Total: {record.total_hours}")

        else:
            print(f"ℹ️  {clean_name} already has full attendance for today.")
            return

        try:
            db.session.commit()
            print(f"   DB saved successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"   DB error: {e}")

def _calc_hours(r):
    total = 0
    try:
        if r.in1 and r.out1:
            t1 = (datetime.combine(date.today(), r.out1) -
                  datetime.combine(date.today(), r.in1)).seconds
            total += t1
        if r.in2 and r.out2:
            t2 = (datetime.combine(date.today(), r.out2) -
                  datetime.combine(date.today(), r.in2)).seconds
            total += t2
    except:
        pass
    h, m = divmod(total // 60, 60)
    return f"{h}h {m}m"

# ── Video stream generator ────────────────────────────────────────
def generate_frames(app):
    cap         = get_camera()
    last_marked = {}  # name → timestamp (cooldown per person)

    while True:
        with camera_lock:
            success, frame = cap.read()
        if not success:
            print("Camera read failed, retrying...")
            time.sleep(0.5)
            continue

        # Recognize faces in frame
        name, frame = recognize_frame(frame)

        # Mark attendance with 15-second cooldown per person
        if name and name not in ("Unknown", "No model"):
            now_ts = time.time()
            last   = last_marked.get(name, 0)
            if (now_ts - last) > 15:
                last_marked[name] = now_ts
                # Run DB write in a separate thread with app context
                t = threading.Thread(
                    target=mark_attendance,
                    args=(name, app),
                    daemon=True
                )
                t.start()

        # Encode and stream frame
        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            continue
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               buffer.tobytes() + b"\r\n")

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
    data = [{
        "name":  r.student.name,
        "roll":  r.student.roll_no,
        "in1":   str(r.in1  or ""),
        "out1":  str(r.out1 or ""),
        "in2":   str(r.in2  or ""),
        "out2":  str(r.out2 or ""),
        "total": r.total_hours or "",
        "status": r.status
    } for r in records]
    return jsonify(data)

@attendance_bp.route("/retrain")
@login_required
def retrain():
    train_model()
    return jsonify({"status": "Model retrained successfully!"})