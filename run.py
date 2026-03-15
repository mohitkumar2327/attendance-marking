from app import create_app
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = create_app()

# Daily scheduler — runs at 6 PM to send absent alerts
def scheduled_jobs():
    with app.app_context():
        from app.notifications.notify import send_absent_alerts, send_daily_summary
        send_absent_alerts()
        send_daily_summary("admin@yourschool.com")  # ← change this

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_jobs, "cron", hour=18, minute=0)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)


### `.env` file (create this in root folder)

SECRET_KEY=your-very-secret-key-here
MAIL_USERNAME=yourschool@gmail.com
MAIL_PASSWORD=your-gmail-app-password
# In run.py — configure multiple cameras
CAMERA_ZONES = {
    0: "Main Gate",      # camera index 0
    1: "Staff Entrance", # camera index 1
    2: "Library",        # camera index 2
}