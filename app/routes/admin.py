from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Student, Attendance
from datetime import date

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    today         = date.today()
    total         = Student.query.count()
    present_today = Attendance.query.filter_by(date=today).count()
    absent_today  = total - present_today
    recent        = Attendance.query.filter_by(date=today).limit(10).all()

    return render_template("dashboard.html",
                           total=total,
                           present=present_today,
                           absent=absent_today,
                           recent=recent,
                           today=today)
