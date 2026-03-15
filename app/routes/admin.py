from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Student, Attendance, Settings
from datetime import date

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    today         = date.today()
    total         = Student.query.count()
    all_records   = Attendance.query.filter_by(date=today).all()
    present_today = len(all_records)
    absent_today  = total - present_today
    late_today    = sum(1 for r in all_records if r.status == "Late")
    recent        = all_records[:15]

    # Get settings from DB
    s = Settings.query.first()
    if s:
        inst_type = s.institution_type
        if inst_type == "school":
            late_time_str = s.school_late_time
        elif inst_type == "office":
            late_time_str = s.office_late_time
        else:
            late_time_str = s.college_late_time
        inst_name = s.institution_name
    else:
        inst_type     = "college"
        late_time_str = "09:10"
        inst_name     = "My Institution"

    # Convert to 12-hour format for display
    try:
        h, m          = map(int, late_time_str.split(":"))
        suffix        = "AM" if h < 12 else "PM"
        h12           = h if h <= 12 else h - 12
        late_time_disp = f"{h12:02d}:{m:02d} {suffix}"
    except:
        late_time_disp = late_time_str

    return render_template("dashboard.html",
                           total=total,
                           present=present_today,
                           absent=absent_today,
                           late=late_today,
                           recent=recent,
                           today=today,
                           institution_type=inst_type,
                           institution_name=inst_name,
                           late_time=late_time_disp)