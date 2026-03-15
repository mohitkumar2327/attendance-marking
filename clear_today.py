from app import create_app
from app.models import Attendance, db
from datetime import date

app = create_app()
with app.app_context():
    today   = date.today()
    deleted = Attendance.query.filter_by(date=today).delete()
    db.session.commit()
    print(f"Cleared {deleted} attendance records for today ({today})")
    print("Fresh start — run: python run.py")