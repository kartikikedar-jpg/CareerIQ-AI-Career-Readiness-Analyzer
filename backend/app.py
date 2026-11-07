from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "docx"}

SKILLS_LIST = [
    "Python", "Java", "SQL", "HTML", "CSS",
    "JavaScript", "React", "Flask", "Django",
    "Pandas", "NumPy", "Excel", "Power BI",
    "Machine Learning"
]


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# Extract text from PDF and DOCX
def extract_resume_text(file_path):
    text = ""

    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    elif file_path.lower().endswith(".docx"):
        document = Document(file_path)

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

    return text


# Detect skills
def detect_skills(text):
    detected_skills = []

    for skill in SKILLS_LIST:
        if skill.lower() in text.lower():
            detected_skills.append(skill)

    return detected_skills

# recommend course

def recommend_courses(missing_skills):

    course_data = {
        "Python": "Python for Beginners",
        "Java": "Java Programming Fundamentals",
        "SQL": "SQL for Data Analysis",
        "HTML": "HTML and CSS Web Development",
        "CSS": "CSS Styling Fundamentals",
        "JavaScript": "JavaScript for Beginners",
        "React": "React JS Complete Course",
        "Flask": "Flask Web Development",
        "Django": "Django for Beginners",
        "Pandas": "Python Pandas Tutorial",
        "NumPy": "NumPy for Data Science",
        "Excel": "Microsoft Excel Fundamentals",
        "Power BI": "Power BI for Beginners",
        "Machine Learning": "Machine Learning Basics"
    }

    recommendations = []

    for skill in missing_skills:
        if skill in course_data:
            recommendations.append(course_data[skill])

    return recommendations


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        if "resume" not in request.files:
            return "Resume file not found!"

        file = request.files["resume"]
        job_description = request.form.get("job_description", "")

        if file.filename == "":
            return "Please select a resume!"

        if not job_description.strip():
            return "Please enter a target job description!"

        if not allowed_file(file.filename):
            return "Only PDF and DOCX files are allowed!"

        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Resume analysis
        resume_text = extract_resume_text(file_path)

        if not resume_text.strip():
            return "No readable text found in this resume."

        resume_skills = detect_skills(resume_text)

        # Job description analysis
        required_skills = detect_skills(job_description)

        # Missing skills
        missing_skills = [
            skill for skill in required_skills
            if skill not in resume_skills
        ]

        # Match percentage
        if required_skills:
            match_percentage = round(
                (len([s for s in required_skills if s in resume_skills])
                 / len(required_skills)) * 100
            )
        else:
            match_percentage = 0

        return render_template(
            "result.html",
            resume_text=resume_text,
            detected_skills=resume_skills,
            required_skills=required_skills,
            missing_skills=missing_skills,
            match_percentage=match_percentage
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)