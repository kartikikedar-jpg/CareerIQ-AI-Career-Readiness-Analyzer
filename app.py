
import os
import re
import sqlite3
from io import BytesIO

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, send_file
)

from werkzeug.security import (
    generate_password_hash, check_password_hash
)
from werkzeug.utils import secure_filename

from PyPDF2 import PdfReader
from docx import Document

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from db import get_db_connection, init_db


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "docx"}

app = Flask(__name__)
app.secret_key = "CareerIQ-Change-This-Secret-Key"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


SKILLS_LIST = [
    "Python", "Java", "C", "C++", "SQL",
    "HTML", "CSS", "JavaScript", "React",
    "Flask", "Django", "Pandas", "NumPy",
    "Excel", "Power BI", "Machine Learning",
    "Data Analysis", "Data Visualization",
    "Statistics", "Matplotlib", "Seaborn",
    "Scikit-learn", "Deep Learning",
    "Tableau", "Git", "GitHub",
    "Data Structures", "Algorithms",
    "MySQL", "MongoDB"
]


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def extract_resume_text(filepath):
    extension = filepath.rsplit(".", 1)[1].lower()

    if extension == "pdf":
        reader = PdfReader(filepath)
        return " ".join(
            page.extract_text() or "" for page in reader.pages
        )

    if extension == "docx":
        document = Document(filepath)
        return " ".join(
            paragraph.text for paragraph in document.paragraphs
        )

    return ""


def detect_skills(text):
    found = []

    for skill in SKILLS_LIST:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)

    return found


def calculate_similarity(resume_text, job_description):
    if not resume_text.strip() or not job_description.strip():
        return 0

    try:
        vectorizer = TfidfVectorizer(stop_words="english")

        matrix = vectorizer.fit_transform([
            resume_text,
            job_description
        ])

        score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]

        return round(score * 100, 2)

    except ValueError:
        return 0


def readiness_level(percentage):
    if percentage >= 80:
        return "Excellent"
    elif percentage >= 60:
        return "Good"
    elif percentage >= 40:
        return "Intermediate"
    return "Needs Improvement"


def login_required():
    return session.get("student_id") is not None


def admin_required():
    return session.get("admin_logged_in") is True


# Initialize database
init_db()


# Create or update default admin account
def setup_admin():
    conn = get_db_connection()

    try:
        admin = conn.execute(
            "SELECT id FROM admins WHERE LOWER(username) = ?",
            ("admin@gmail.com",)
        ).fetchone()

        password_hash = generate_password_hash("admin123")

        if admin:
            conn.execute("""
                UPDATE admins
                SET password_hash = ?
                WHERE id = ?
            """, (password_hash, admin["id"]))
        else:
            conn.execute("""
                INSERT INTO admins(username, password_hash)
                VALUES (?, ?)
            """, ("admin@gmail.com", password_hash))

        conn.commit()

    finally:
        conn.close()


setup_admin()


# Common Login Page
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()

        try:
            admin = conn.execute(
                "SELECT * FROM admins WHERE LOWER(username) = ?",
                (email,)
            ).fetchone()

            if admin and check_password_hash(
                admin["password_hash"], password
            ):
                session.clear()
                session["admin_logged_in"] = True
                session["admin_username"] = admin["username"]

                return redirect("/admin/dashboard")

            student = conn.execute(
                "SELECT * FROM students WHERE LOWER(email) = ?",
                (email,)
            ).fetchone()

            if student and check_password_hash(
                student["password_hash"], password
            ):
                session.clear()
                session["student_id"] = student["id"]
                session["student_name"] = student["name"]

                return redirect("/")

        finally:
            conn.close()

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# Student Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return render_template(
                "signup.html",
                error="Please fill all fields."
            )

        if len(password) < 8:
            return render_template(
                "signup.html",
                error="Password must contain at least 8 characters."
            )

        conn = get_db_connection()

        try:
            existing = conn.execute(
                "SELECT id FROM students WHERE LOWER(email) = ?",
                (email,)
            ).fetchone()

            if existing:
                return render_template(
                    "signup.html",
                    error="Email already registered. Please login."
                )

            conn.execute("""
                INSERT INTO students(name, email, password_hash)
                VALUES (?, ?, ?)
            """, (
                name,
                email,
                generate_password_hash(password)
            ))

            conn.commit()

            return redirect("/login")

        except sqlite3.IntegrityError:
            conn.rollback()

            return render_template(
                "signup.html",
                error="This email is already registered."
            )

        finally:
            conn.close()

    return render_template("signup.html")


# Main Student Analyzer
@app.route("/", methods=["GET", "POST"])
def home():

    if not login_required():
        return redirect("/login")

    if request.method == "POST":

        if "resume" not in request.files:
            return "Please upload a resume."

        resume = request.files["resume"]
        job_description = request.form.get("job_description", "").strip()

        if not resume.filename or not job_description:
            return "Please provide resume and job description."

        if not allowed_file(resume.filename):
            return "Only PDF and DOCX files are allowed."

        filename = secure_filename(resume.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        resume.save(filepath)

        try:
            resume_text = extract_resume_text(filepath)

            detected_skills = detect_skills(resume_text)
            required_skills = detect_skills(job_description)

            matched_skills = [
                skill for skill in required_skills
                if skill in detected_skills
            ]

            missing_skills = [
                skill for skill in required_skills
                if skill not in detected_skills
            ]

            if required_skills:
                match_percentage = round(
                    len(matched_skills) / len(required_skills) * 100, 2
                )
            else:
                match_percentage = 0

            text_similarity = calculate_similarity(
                resume_text, job_description
            )

            level = readiness_level(match_percentage)

            recommendations = [
                "https://www.youtube.com/results?search_query="
                + skill.replace(" ", "+")
                + "+tutorial"
                for skill in missing_skills
            ]

            improvement_tips = [
                {
                    "skill": skill,
                    "tip": "Learn and practice " + skill
                }
                for skill in missing_skills
            ]

            learning_roadmap = [
                {
                    "skill": skill,
                    "duration": "1-2 weeks",
                    "levels": "Beginner to Intermediate"
                }
                for skill in missing_skills
            ]

            conn = get_db_connection()

            try:
                cursor = conn.execute("""
                    INSERT INTO analyses(
                        resume_filename,
                        match_percentage,
                        text_similarity,
                        readiness_level,
                        detected_skills,
                        required_skills,
                        matched_skills,
                        missing_skills,
                        user_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    filename,
                    match_percentage,
                    text_similarity,
                    level,
                    ", ".join(detected_skills),
                    ", ".join(required_skills),
                    ", ".join(matched_skills),
                    ", ".join(missing_skills),
                    session["student_id"]
                ))

                analysis_id = cursor.lastrowid

                conn.execute("""
                    INSERT INTO resume_uploads(
                        user_id, resume_filename, analysis_id
                    )
                    VALUES (?, ?, ?)
                """, (
                    session["student_id"],
                    filename,
                    analysis_id
                ))

                conn.commit()

            finally:
                conn.close()

            session["career_report"] = {
                "match_percentage": match_percentage,
                "text_similarity": text_similarity,
                "readiness_level": level,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "detected_skills": detected_skills,
                "required_skills": required_skills,
                "recommendations": recommendations,
                "improvement_tips": improvement_tips,
                "learning_roadmap": learning_roadmap,
                "resume_text": resume_text
            }

            return redirect("/result")

        except Exception as error:
            if os.path.exists(filepath):
                os.remove(filepath)

            return "Resume analysis error: " + str(error)

    return render_template("index.html")


# Result Page
@app.route("/result")
def result():

    if not login_required():
        return redirect("/login")

    report = session.get("career_report")

    if not report:
        return redirect("/")

    return render_template("result.html", **report)


# PDF Report
@app.route("/download-report")
def download_report():

    if not login_required():
        return redirect("/login")

    report = session.get("career_report")

    if not report:
        return redirect("/")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, 800, "CareerIQ Analysis Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(
        50, 760,
        "Match Percentage: "
        + str(report["match_percentage"]) + "%"
    )

    pdf.drawString(
        50, 735,
        "Readiness Level: " + report["readiness_level"]
    )

    y = 690

    pdf.drawString(50, y, "Matched Skills:")
    y -= 20

    for skill in report["matched_skills"]:
        if y < 60:
            pdf.showPage()
            y = 800

        pdf.drawString(70, y, skill)
        y -= 18

    y -= 15
    pdf.drawString(50, y, "Missing Skills:")
    y -= 20

    for skill in report["missing_skills"]:
        if y < 60:
            pdf.showPage()
            y = 800

        pdf.drawString(70, y, skill)
        y -= 18

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="CareerIQ_Report.pdf",
        mimetype="application/pdf"
    )


# Admin URL redirects to common login
@app.route("/admin")
def admin_login():
    return redirect("/login")


# Admin Dashboard
@app.route("/admin/dashboard")
def admin_dashboard():

    if not admin_required():
        return redirect("/login")

    conn = get_db_connection()

    try:
        total_students = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        total_analyses = conn.execute(
            "SELECT COUNT(*) FROM analyses"
        ).fetchone()[0]

        total_uploads = conn.execute(
            "SELECT COUNT(*) FROM resume_uploads"
        ).fetchone()[0]

        students = conn.execute("""
            SELECT id, name, email, created_at
            FROM students ORDER BY id DESC
        """).fetchall()

        analyses = conn.execute("""
            SELECT * FROM analyses ORDER BY id DESC
        """).fetchall()

    finally:
        conn.close()

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_analyses=total_analyses,
        total_uploads=total_uploads,
        students=students,
        analyses=analyses
    )


# Student Logout
@app.route("/logout")
@app.route("/student_logout", endpoint="student_logout")
def logout():
    session.clear()
    return redirect("/login")


# Admin Logout
@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/login")


@app.errorhandler(413)
def file_too_large(error):
    return "File too large. Maximum size is 5 MB.", 413


if __name__ == "__main__":
    app.run(debug=True)
