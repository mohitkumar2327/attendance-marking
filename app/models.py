"""from . import db
from flask_login import UserMixin
from datetime import datetime

class Admin(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role     = db.Column(db.String(20), default="admin")  # admin / teacher / viewer

class Student(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    roll_no    = db.Column(db.String(30), unique=True, nullable=False)
    department = db.Column(db.String(100))
    year       = db.Column(db.String(10))
    email      = db.Column(db.String(120))          # for alerts to student
    parent_email = db.Column(db.String(120))        # for alerts to parents
    photo_path = db.Column(db.String(200))
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    attendance = db.relationship("Attendance", backref="student", lazy=True)

class Attendance(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    date       = db.Column(db.Date, default=datetime.utcnow().date)
    in1        = db.Column(db.Time, nullable=True)
    out1       = db.Column(db.Time, nullable=True)
    in2        = db.Column(db.Time, nullable=True)
    out2       = db.Column(db.Time, nullable=True)
    total_hours = db.Column(db.String(20), nullable=True)
    status     = db.Column(db.String(20), default="Present")  # Present/Absent/Late"""

from . import db
from flask_login import UserMixin
from datetime import datetime

class Admin(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role     = db.Column(db.String(20), default="admin")

class Student(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False)
    roll_no      = db.Column(db.String(30),  unique=True, nullable=False)
    department   = db.Column(db.String(100))
    year         = db.Column(db.String(20))
    email        = db.Column(db.String(120))
    parent_email = db.Column(db.String(120))
    person_type  = db.Column(db.String(20), default="student")  # student / employee
    photo_path   = db.Column(db.String(200))
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    attendance   = db.relationship("Attendance", backref="student", lazy=True)

class Attendance(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    student_id  = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    date        = db.Column(db.Date,    default=datetime.utcnow().date)
    in1         = db.Column(db.Time,    nullable=True)
    out1        = db.Column(db.Time,    nullable=True)
    in2         = db.Column(db.Time,    nullable=True)
    out2        = db.Column(db.Time,    nullable=True)
    total_hours = db.Column(db.String(20), nullable=True)
    status      = db.Column(db.String(20), default="Present")