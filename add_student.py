from app import create_app
from app.models import Student, db

app = create_app()
with app.app_context():
    # Check if already exists
    existing = Student.query.filter_by(roll_no="001").first()
    if existing:
        print(f"Student already exists: {existing.name}")
    else:
        student = Student(
            name         = "A.ram",      # must match folder name after underscore
            roll_no      = "001",
            department   = "Computer Science",
            year         = "1st Year",
            email        = "",
            parent_email = ""
        )
        db.session.add(student)
        db.session.commit()
        print(f"Student added! ID: {student.id}  Name: {student.name}")