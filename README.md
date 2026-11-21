
# CareerIQ – AI Career Readiness & Skill Gap Analyzer

<p align="center">
  <b>An AI-powered platform to analyze career readiness and identify skill gaps.</b>
</p>

---

## About the Project

CareerIQ is an AI-powered career readiness and skill gap analysis system designed to help students and job seekers understand their current skills and prepare for their desired careers.

The system analyzes uploaded resumes against a target job description and generates a personalized career readiness report.

## Key Features

- User Registration and Login
- Admin Login and Dashboard
- Resume Upload (PDF and DOCX)
- Job Description Analysis
- Automatic Skill Detection
- Skill Gap Identification
- Career Readiness Score
- Personalized Course Recommendations
- Career Improvement Roadmap
- Downloadable PDF Report

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend Programming |
| Flask | Web Framework |
| HTML5 | Webpage Structure |
| CSS3 | Website Styling |
| JavaScript | Frontend Interactivity |
| SQLite | Database Management |
| ReportLab | PDF Report Generation |
| PyPDF | PDF Text Extraction |
| python-docx | DOCX File Processing |

## Project Structure

```text
CareerIQ/
│
├── backend/
├── dataset/
├── screenshots/
├── static/
│   └── images/
├── templates/
│   ├── admin_dashboard.html
│   ├── admin_login.html
│   ├── index.html
│   ├── login.html
│   ├── result.html
│   └── signup.html
│
├── app.py
├── db.py
├── requirements.txt
├── reset_admin.py
├── start.bat
└── README.md
```

## How CareerIQ Works

1. User creates an account or logs in.
2. User uploads their resume.
3. User enters the target job description.
4. CareerIQ extracts skills from the resume.
5. The system compares existing skills with required skills.
6. It calculates a career readiness score.
7. A personalized report is generated with missing skills and recommendations.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/kartikikedar-jpg/CareerIQ-AI-Career-Readiness-Analyzer.git
```

### 2. Open the Project Folder

```bash
cd CareerIQ-AI-Career-Readiness-Analyzer
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate Virtual Environment

```bash
.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/login
```

## Screenshots

Project screenshots are available in the `screenshots` folder.

## Project Objective

The main objective of CareerIQ is to bridge the gap between students' existing skills and industry requirements by providing personalized career insights and actionable learning recommendations.

## Future Scope

- Integration of advanced AI-based resume analysis.
- More comprehensive job role recommendations.
- Integration with online learning platforms.
- Advanced career analytics dashboard.
- Support for additional technical and professional skills.

---

<p align="center">
  <b>CareerIQ – Analyze Your Skills. Discover Your Potential. Build Your Career.</b>
</p>
