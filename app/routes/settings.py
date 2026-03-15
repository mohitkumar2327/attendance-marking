from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Settings, db
from datetime import datetime

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

def get_settings():
    s = Settings.query.first()
    if not s:
        s = Settings()
        db.session.add(s)
        db.session.commit()
    return s

@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    s = get_settings()

    if request.method == "POST":
        s.institution_name  = request.form.get("institution_name",  "My Institution")
        s.institution_type  = request.form.get("institution_type",  "college")
        s.school_late_time  = request.form.get("school_late_time",  "08:30")
        s.college_late_time = request.form.get("college_late_time", "09:10")
        s.office_late_time  = request.form.get("office_late_time",  "08:30")
        s.cooldown_seconds  = int(request.form.get("cooldown_seconds", 300))
        s.updated_at        = datetime.utcnow()
        db.session.commit()

        # Update recognize.py cooldown live
        try:
            import app.face.recognize as rec
            rec.COOLDOWN_SECONDS = s.cooldown_seconds
            print(f"Cooldown updated to {s.cooldown_seconds}s live")
        except Exception as e:
            print(f"Live cooldown update failed: {e}")

        flash("Settings saved successfully!", "success")
        return redirect(url_for("settings.index"))

    return render_template("settings.html", s=s)