from flask import Flask, render_template, request, session, send_file
import os
import re
from io import BytesIO

from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from xml.sax.saxutils import escape


app = Flask(__name__)
app.secret_key = "career_analyzer_demo_key"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "docx"}


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


SKILL_ALIASES = {
    "Python": ["python programming", "python language"],
    "Java": ["java programming"],
    "C++": ["cpp", "c plus plus"],
    "SQL": ["structured query language"],
    "HTML": ["html5"],
    "CSS": ["css3", "cascading style sheets"],
    "JavaScript": ["js", "javascript programming"],
    "React": ["react.js", "reactjs"],
    "Flask": ["flask framework"],
    "Django": ["django framework"],
    "Pandas": ["pandas library"],
    "NumPy": ["numpy library"],
    "Excel": ["ms excel", "microsoft excel"],
    "Power BI": ["powerbi"],
    "Machine Learning": ["ml", "machine learning algorithms"],
    "Data Analysis": ["data analytics", "data analyzing"],
    "Data Visualization": ["data viz"],
    "Scikit-learn": ["sklearn"],
    "Matplotlib": ["matplotlib library"],
    "Seaborn": ["seaborn library"],
    "Deep Learning": ["dl"],
    "GitHub": ["github repository"],
    "MySQL": ["mysql database"],
    "MongoDB": ["mongo database"]
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def extract_resume_text(filepath):

    extension = filepath.rsplit(".", 1)[1].lower()
    text = ""

    if extension == "pdf":
        reader = PdfReader(filepath)

        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"

    elif extension == "docx":
        document = Document(filepath)

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

    return text


def detect_skills(text):

    detected_skills = []
    text = text.lower()

    for skill in SKILLS_LIST:

        keywords = [skill.lower()]
        keywords.extend(
            alias.lower()
            for alias in SKILL_ALIASES.get(skill, [])
        )

        for keyword in keywords:

            pattern = (
                r"(?<!\w)"
                + re.escape(keyword)
                + r"(?!\w)"
            )

            if re.search(pattern, text):
                detected_skills.append(skill)
                break

    if "C++" in detected_skills and "C" in detected_skills:
        detected_skills.remove("C")

    return detected_skills


# NLP: Compare resume and job description using TF-IDF
def calculate_text_similarity(resume_text, job_description):

    if not resume_text.strip() or not job_description.strip():
        return 0

    try:
        documents = [resume_text, job_description]

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000
        )

        tfidf_matrix = vectorizer.fit_transform(documents)

        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        return round(float(similarity) * 100, 2)

    except ValueError:
        return 0


def recommend_courses(missing_skills):

    course_database = {
        "Python": "Python Programming for Beginners",
        "Java": "Java Programming Fundamentals",
        "C": "C Programming Fundamentals",
        "C++": "C++ Programming Course",
        "SQL": "SQL and Database Management",
        "HTML": "HTML Web Development",
        "CSS": "CSS Styling Fundamentals",
        "JavaScript": "JavaScript for Web Development",
        "React": "React JS Complete Course",
        "Flask": "Flask Web Development",
        "Django": "Django Web Development",
        "Pandas": "Data Analysis with Pandas",
        "NumPy": "NumPy for Data Science",
        "Excel": "Microsoft Excel for Data Analysis",
        "Power BI": "Power BI Data Visualization",
        "Machine Learning": "Machine Learning Fundamentals",
        "Data Analysis": "Data Analysis Fundamentals",
        "Data Visualization": "Data Visualization Course",
        "Statistics": "Statistics for Data Science",
        "Matplotlib": "Data Visualization with Matplotlib",
        "Seaborn": "Data Visualization with Seaborn",
        "Scikit-learn": "Machine Learning with Scikit-learn",
        "Deep Learning": "Deep Learning Fundamentals",
        "Tableau": "Tableau Data Visualization",
        "Git": "Git Version Control",
        "GitHub": "GitHub for Beginners",
        "Data Structures": "Data Structures Fundamentals",
        "Algorithms": "Algorithms Fundamentals",
        "MySQL": "MySQL Database Course",
        "MongoDB": "MongoDB Fundamentals"
    }

    return [
        course_database.get(skill, skill + " Fundamentals")
        for skill in missing_skills
    ]


def generate_suggestions(missing_skills):

    suggestions = {
        "Python": "Practice Python programming and solve coding problems.",
        "Java": "Learn Java and object-oriented programming.",
        "C": "Practice basic C programming.",
        "C++": "Learn C++ and object-oriented programming.",
        "SQL": "Practice SQL queries and database operations.",
        "HTML": "Build web pages using HTML.",
        "CSS": "Practice website styling using CSS.",
        "JavaScript": "Build interactive web pages.",
        "React": "Create small projects using React.",
        "Flask": "Build web applications using Flask.",
        "Django": "Practice backend development using Django.",
        "Pandas": "Practice data manipulation using Pandas.",
        "NumPy": "Learn numerical computing using NumPy.",
        "Excel": "Practice spreadsheet analysis.",
        "Power BI": "Create dashboards using Power BI.",
        "Machine Learning": "Study machine learning algorithms.",
        "Data Analysis": "Practice analyzing real-world datasets.",
        "Data Visualization": "Learn to create meaningful charts.",
        "Statistics": "Strengthen your statistical concepts.",
        "Matplotlib": "Practice plotting graphs with Matplotlib.",
        "Seaborn": "Create statistical visualizations.",
        "Scikit-learn": "Build ML models using Scikit-learn.",
        "Deep Learning": "Study neural networks.",
        "Tableau": "Practice creating dashboards.",
        "Git": "Learn version control using Git.",
        "GitHub": "Practice managing projects on GitHub.",
        "Data Structures": "Practice arrays, stacks, queues and trees.",
        "Algorithms": "Solve problems using algorithms.",
        "MySQL": "Practice database queries using MySQL.",
        "MongoDB": "Learn NoSQL database operations."
    }

    return [
        {
            "skill": skill,
            "tip": suggestions.get(
                skill,
                "Practice this skill through small projects."
            )
        }
        for skill in missing_skills
    ]

def generate_learning_roadmap(missing_skills):
    roadmap = []

    for skill in missing_skills:
        roadmap.append({
            "skill": skill,
            "duration": "2-3 Weeks",
            "levels": [
                "Beginner: Learn basic concepts",
                "Intermediate: Practice with exercises",
                "Advanced: Build a practical project"
            ]
        })

    return roadmap

def calculate_readiness_level(match_percentage):

    if match_percentage >= 80:
        return "Job Ready"
    elif match_percentage >= 60:
        return "Almost Ready"
    elif match_percentage >= 40:
        return "Developing Skills"
    else:
        return "Beginner"


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        if "resume" not in request.files:
            return render_template(
                "index.html",
                error="Please upload your resume."
            )

        resume_file = request.files["resume"]

        job_description = request.form.get(
            "job_description", ""
        ).strip()

        if resume_file.filename == "":
            return render_template(
                "index.html",
                error="Please select a resume file."
            )

        if not job_description:
            return render_template(
                "index.html",
                error="Please enter a target job description."
            )

        if not allowed_file(resume_file.filename):
            return render_template(
                "index.html",
                error="Only PDF and DOCX files are allowed."
            )

        filename = secure_filename(resume_file.filename)
        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"], filename
        )

        resume_file.save(filepath)

        try:
            resume_text = extract_resume_text(filepath)

            if not resume_text.strip():
                return render_template(
                    "index.html",
                    error="No readable text found in the resume."
                )

        except Exception:
            return render_template(
                "index.html",
                error="Unable to read the resume. Please check the file."
            )

        # Existing skill analysis
        resume_skills = detect_skills(resume_text)
        required_skills = detect_skills(job_description)

        resume_skills = list(dict.fromkeys(resume_skills))
        required_skills = list(dict.fromkeys(required_skills))

        matched_skills = [
            skill for skill in required_skills
            if skill in resume_skills
        ]

        missing_skills = [
            skill for skill in required_skills
            if skill not in resume_skills
        ]

        if required_skills:
            match_percentage = round(
                len(matched_skills) / len(required_skills) * 100
            )
        else:
            match_percentage = 0

        # New NLP similarity analysis
        text_similarity = calculate_text_similarity(
            resume_text,
            job_description
        )

        recommendations = recommend_courses(missing_skills)
        improvement_tips = generate_suggestions(missing_skills)

        learning_roadmap = generate_learning_roadmap(missing_skills)

        readiness_level = calculate_readiness_level(
            match_percentage
        )

        # Save report data for PDF download
        session["career_report"] = {
            "match_percentage": match_percentage,
            "text_similarity": text_similarity,
            "readiness_level": readiness_level,
            "detected_skills": resume_skills,
            "required_skills": required_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendations": recommendations,
            "improvement_tips": improvement_tips
        }

        return render_template(
            "result.html",
            resume_text=resume_text,
            detected_skills=resume_skills,
            required_skills=required_skills,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            match_percentage=match_percentage,
            text_similarity=text_similarity,
            recommendations=recommendations,
            improvement_tips=improvement_tips,
            readiness_level=readiness_level,
            learning_roadmap=learning_roadmap
        )

    return render_template("index.html")


# PDF Download Route
@app.route("/download-report")
def download_report():

    report = session.get("career_report")

    if not report:
        return "Please analyze a resume before downloading the report.", 400

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph("AI Career Readiness Report", styles["Title"])
    )
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Skill Match Score: {report['match_percentage']}%",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            f"NLP Text Similarity: {report['text_similarity']}%",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            f"Readiness Level: {escape(report['readiness_level'])}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 15))

    data = [
        ["Category", "Count"],
        ["Required Skills", str(len(report["required_skills"]))],
        ["Matched Skills", str(len(report["matched_skills"]))],
        ["Missing Skills", str(len(report["missing_skills"]))]
    ]

    table = Table(data, colWidths=[250, 150])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#625BD0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 9)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    sections = [
        ("Detected Resume Skills", report["detected_skills"]),
        ("Matched Skills", report["matched_skills"]),
        ("Missing Skills", report["missing_skills"]),
        ("Recommended Courses", report["recommendations"])
    ]

    for heading, items in sections:

        elements.append(
            Paragraph(heading, styles["Heading2"])
        )

        if items:
            for item in items:
                elements.append(
                    Paragraph(
                        "• " + escape(str(item)),
                        styles["Normal"]
                    )
                )
        else:
            elements.append(
                Paragraph("None", styles["Normal"])
            )

        elements.append(Spacer(1, 12))

    elements.append(
        Paragraph("Improvement Roadmap", styles["Heading2"])
    )

    for item in report["improvement_tips"]:

        elements.append(
            Paragraph(
                f"<b>{escape(item['skill'])}</b>: "
                f"{escape(item['tip'])}",
                styles["Normal"]
            )
        )

        elements.append(Spacer(1, 8))

    pdf.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Career_Readiness_Report.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)