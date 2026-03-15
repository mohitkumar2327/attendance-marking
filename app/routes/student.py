"""from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Student, db
from app.face.enroll import save_face_images
import os

student_bp = Blueprint("student", __name__, url_prefix="/students")

@student_bp.route("/")
@login_required
def list_students():
    students = Student.query.all()
    return render_template("students.html", students=students)

@student_bp.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        student = Student(
            name         = request.form["name"],
            roll_no      = request.form["roll_no"],
            department   = request.form["department"],
            year         = request.form["year"],
            email        = request.form["email"],
            parent_email = request.form["parent_email"]
        )
        db.session.add(student)
        db.session.commit()

        # Save face images from uploaded photos
        files = request.files.getlist("photos")
        save_face_images(student.id, student.name, files)

        flash(f"Student {student.name} registered successfully!", "success")
        return redirect(url_for("student.list_students"))

    return render_template("register_student.html")

@student_bp.route("/delete/<int:id>")
@login_required
def delete(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted.", "info")
    return redirect(url_for("student.list_students"))"""


from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, send_file)
from flask_login import login_required
from app.models import Student, db
from app.face.enroll import save_face_images
import pandas as pd
import io
import os

student_bp = Blueprint("student", __name__, url_prefix="/students")

# ── List all ──────────────────────────────────────────────────────
@student_bp.route("/")
@login_required
def list_students():
    filter_type = request.args.get("type", "all")
    if filter_type == "student":
        people = Student.query.filter_by(person_type="student").all()
    elif filter_type == "employee":
        people = Student.query.filter_by(person_type="employee").all()
    else:
        people = Student.query.all()

    students  = Student.query.filter_by(person_type="student").count()
    employees = Student.query.filter_by(person_type="employee").count()
    return render_template("students.html",
                           people=people,
                           filter_type=filter_type,
                           total_students=students,
                           total_employees=employees)

# ── Register one person ───────────────────────────────────────────
@student_bp.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        # Check duplicate roll number
        existing = Student.query.filter_by(
            roll_no=request.form["roll_no"]
        ).first()
        if existing:
            flash(f"Roll No {request.form['roll_no']} already exists!", "danger")
            return redirect(url_for("student.register"))

        person = Student(
            name         = request.form["name"],
            roll_no      = request.form["roll_no"],
            department   = request.form["department"],
            year         = request.form.get("year", "N/A"),
            email        = request.form.get("email", ""),
            parent_email = request.form.get("parent_email", ""),
            person_type  = request.form.get("person_type", "student")
        )
        db.session.add(person)
        db.session.commit()

        # Save face photos
        files = request.files.getlist("photos")
        if files and files[0].filename:
            save_face_images(person.id, person.name, files)
            flash(f"{person.name} registered with face photos!", "success")
        else:
            flash(f"{person.name} registered. Add face photos via "
                  f"capture_faces.py", "warning")

        return redirect(url_for("student.list_students"))

    return render_template("register_student.html")

# ── Excel import ──────────────────────────────────────────────────
@student_bp.route("/import", methods=["GET", "POST"])
@login_required
def import_excel():
    if request.method == "POST":
        file = request.files.get("excel_file")
        if not file or not file.filename.endswith((".xlsx", ".xls")):
            flash("Please upload a valid Excel file (.xlsx or .xls)", "danger")
            return redirect(url_for("student.import_excel"))

        try:
            df = pd.read_excel(file)
            required_cols = {"name", "roll_no"}
            if not required_cols.issubset(df.columns.str.lower()):
                flash("Excel must have at least 'name' and 'roll_no' columns!",
                      "danger")
                return redirect(url_for("student.import_excel"))

            # Normalize column names
            df.columns = df.columns.str.lower().str.strip()

            added    = 0
            skipped  = 0
            errors   = []

            for _, row in df.iterrows():
                name    = str(row.get("name",    "")).strip()
                roll_no = str(row.get("roll_no", "")).strip()

                if not name or not roll_no or name == "nan":
                    skipped += 1
                    continue

                # Skip duplicates
                if Student.query.filter_by(roll_no=roll_no).first():
                    skipped += 1
                    errors.append(f"Skipped '{name}' — Roll No {roll_no} "
                                  f"already exists")
                    continue

                person = Student(
                    name         = name,
                    roll_no      = roll_no,
                    department   = str(row.get("department",   "")).strip(),
                    year         = str(row.get("year",         "N/A")).strip(),
                    email        = str(row.get("email",        "")).strip(),
                    parent_email = str(row.get("parent_email", "")).strip(),
                    person_type  = str(row.get("type", "student")).strip().lower()
                )
                db.session.add(person)
                added += 1

            db.session.commit()

            if errors:
                for e in errors[:5]:   # show max 5 warnings
                    flash(e, "warning")

            flash(f"Import complete! Added: {added} | Skipped: {skipped}",
                  "success")

        except Exception as e:
            flash(f"Error reading Excel file: {str(e)}", "danger")

        return redirect(url_for("student.list_students"))

    return render_template("import_excel.html")

# ── Download template ─────────────────────────────────────────────
@student_bp.route("/download_template")
@login_required
def download_template():
    df = pd.DataFrame([
        {
            "name": "John Doe", "roll_no": "CS001",
            "department": "Computer Science", "year": "1st Year",
            "email": "john@email.com", "parent_email": "parent@email.com",
            "type": "student"
        },
        {
            "name": "Mr. Kumar", "roll_no": "EMP001",
            "department": "Administration", "year": "N/A",
            "email": "kumar@school.com", "parent_email": "",
            "type": "employee"
        }
    ])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Students")
    output.seek(0)
    return send_file(
        output,
        download_name="students_import_template.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument"
                 ".spreadsheetml.sheet"
    )

# ── Delete ────────────────────────────────────────────────────────
@student_bp.route("/delete/<int:id>")
@login_required
def delete(id):
    person = Student.query.get_or_404(id)
    name   = person.name
    db.session.delete(person)
    db.session.commit()
    flash(f"{name} deleted successfully.", "info")
    return redirect(url_for("student.list_students"))