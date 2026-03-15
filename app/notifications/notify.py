from flask_mail import Message
from app import mail
from app.models import Student, Attendance
from datetime import date

def send_absent_alerts():
    """Call this daily via scheduler — alerts parents of absent students."""
    today = date.today()
    all_students = Student.query.all()
    present_ids  = {r.student_id for r in Attendance.query.filter_by(date=today).all()}

    for student in all_students:
        if student.id not in present_ids:
            if student.parent_email:
                msg = Message(
                    subject=f"Attendance Alert — {student.name} is Absent Today",
                    recipients=[student.parent_email],
                    body=f"""Dear Parent,

This is to inform you that {student.name} (Roll No: {student.roll_no})
was marked ABSENT on {today}.

Please contact the institution if this is an error.

Regards,
Attendance System"""
                )
                try:
                    mail.send(msg)
                    print(f"Alert sent to {student.parent_email}")
                except Exception as e:
                    print(f"Failed to send alert: {e}")

def send_daily_summary(admin_email):
    """Send daily attendance summary to admin."""
    today   = date.today()
    records = Attendance.query.filter_by(date=today).all()
    total   = Student.query.count()
    present = len(records)
    absent  = total - present

    body = f"""Daily Attendance Summary — {today}

Total Students : {total}
Present        : {present}
Absent         : {absent}
Attendance %   : {round(present/total*100, 1) if total else 0}%
"""
    msg = Message(
        subject=f"Daily Attendance Summary — {today}",
        recipients=[admin_email],
        body=body
    )
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Summary email failed: {e}")