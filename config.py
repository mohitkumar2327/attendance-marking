import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret")
    SQLALCHEMY_DATABASE_URI = "sqlite:///attendance.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email alerts
    MAIL_SERVER   = "smtp.gmail.com"
    MAIL_PORT     = 587
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")

    DATASET_DIR   = "dataset"
    UPLOAD_FOLDER = "dataset"
from datetime import time

# Late coming thresholds — edit these anytime
LATE_TIMINGS = {
    "school":  time(8, 30),   # 8:30 AM
    "college": time(9, 10),   # 9:10 AM
    "office":  time(8, 30),   # 8:30 AM
}

# Set your institution type here
INSTITUTION_TYPE = "college"  # change to "school" or "office"

# INSTITUTION_TYPE = "school"   # 8:30 AM
# INSTITUTION_TYPE = "college"  # 9:10 AM
# INSTITUTION_TYPE = "office"   # 8:30 AM