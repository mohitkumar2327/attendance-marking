from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
from app.models import Attendance, Student, db
from datetime import date, datetime
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.route("/")
@login_required
def index():
    return render_template("reports.html")

@reports_bp.route("/export/excel")
@login_required
def export_excel():
    from_date = request.args.get("from", str(date.today()))
    to_date   = request.args.get("to",   str(date.today()))

    records = Attendance.query.filter(
        Attendance.date.between(from_date, to_date)
    ).all()

    rows = [{
        "Name":        r.student.name,
        "Roll No":     r.student.roll_no,
        "Department":  r.student.department,
        "Date":        str(r.date),
        "IN1":         str(r.in1 or ""),
        "OUT1":        str(r.out1 or ""),
        "IN2":         str(r.in2 or ""),
        "OUT2":        str(r.out2 or ""),
        "Total Hours": r.total_hours or "",
        "Status":      r.status
    } for r in records]

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")
    output.seek(0)

    return send_file(output,
                     download_name=f"attendance_{from_date}_to_{to_date}.xlsx",
                     as_attachment=True,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@reports_bp.route("/export/pdf")
@login_required
def export_pdf():
    from_date = request.args.get("from", str(date.today()))
    to_date   = request.args.get("to",   str(date.today()))

    records = Attendance.query.filter(
        Attendance.date.between(from_date, to_date)
    ).all()

    output = io.BytesIO()
    doc    = SimpleDocTemplate(output, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Attendance Report", styles["Title"]))
    elements.append(Paragraph(f"Period: {from_date} to {to_date}", styles["Normal"]))

    data = [["Name", "Roll No", "Date", "IN1", "OUT1", "IN2", "OUT2", "Total", "Status"]]
    for r in records:
        data.append([
            r.student.name, r.student.roll_no, str(r.date),
            str(r.in1 or ""), str(r.out1 or ""),
            str(r.in2 or ""), str(r.out2 or ""),
            r.total_hours or "", r.status
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
    ]))
    elements.append(table)
    doc.build(elements)
    output.seek(0)

    return send_file(output,
                     download_name=f"attendance_{from_date}.pdf",
                     as_attachment=True,
                     mimetype="application/pdf")