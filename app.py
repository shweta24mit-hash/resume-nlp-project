from flask import Flask, render_template, request, redirect, session
import sqlite3
import pdfplumber
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -----------------------
# Create Database
# -----------------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# SKILLS DATABASE
# -----------------------------
skills_db = [
    "python","java","c","c++","html","css","javascript",
    "machine learning","deep learning","data science",
    "flask","django","sql","mongodb","react","nodejs",
    "android","kotlin","aws","docker","blockchain","solidity",
    "tensorflow","pytorch","git","linux"
]

# -----------------------------
# JOB ROLE DATABASE
# -----------------------------
job_roles = {
    "Software Developer": ["python","java","c","c++","javascript"],
    "Web Developer": ["html","css","javascript","react","nodejs"],
    "Data Scientist": ["python","machine learning","data science"],
    "AI Engineer": ["python","deep learning","tensorflow","pytorch"],
    "Blockchain Developer": ["blockchain","solidity"],
    "Android Developer": ["java","kotlin","android"],
    "Cloud Engineer": ["aws","docker","linux"]
}

# -----------------------------
# EXTRACT TEXT
# -----------------------------
def extract_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.lower()

# -----------------------------
# SKILL EXTRACTION
# -----------------------------
def extract_skills(text):
    found_skills = []
    for skill in skills_db:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            found_skills.append(skill)
    return list(set(found_skills))

# -----------------------------
# JOB RECOMMENDATION
# -----------------------------
def recommend_jobs_with_score(skills):
    results = []

    for job, job_skills in job_roles.items():
        match_count = sum(1 for skill in skills if skill in job_skills)
        score = int((match_count / len(job_skills)) * 100)
        results.append((job, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results

# -----------------------------
# ATS SCORE
# -----------------------------
def calculate_score(skills):
    total_possible = len(skills_db)
    score = int((len(skills) / total_possible) * 100)
    return min(score, 100)

# -----------------------------
# SKILL GAP ANALYSIS
# -----------------------------
def skill_gap_analysis(skills):
    required_skills = {
        "python","sql","machine learning","html","css",
        "javascript","react","nodejs","aws","docker"
    }
    return list(required_skills - set(skills))

# -----------------------------
# SUGGESTIONS
# -----------------------------
def get_suggestions(skills):

    suggestions = []

    if "python" not in skills:
        suggestions.append("Learn Python for better opportunities")

    if "machine learning" not in skills:
        suggestions.append("Add Machine Learning skills")

    if "sql" not in skills:
        suggestions.append("Database knowledge (SQL) is important")

    if len(skills) < 5:
        suggestions.append("Try adding more technical skills")

    return suggestions

# -----------------------
# LOGIN
# -----------------------
@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid Login"

    return render_template("login.html")

# -----------------------
# REGISTER
# -----------------------
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (username, hashed_password)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

# -----------------------
# DASHBOARD
# -----------------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html", user=session["user"])

# -----------------------
# ANALYZE
# -----------------------
@app.route('/analyze', methods=['POST'])
def analyze():

    if "user" not in session:
        return redirect("/")

    file = request.files['resume']

    text = extract_text(file)

    skills = extract_skills(text)

    jobs = recommend_jobs_with_score(skills)

    score = calculate_score(skills)

    missing_skills = skill_gap_analysis(skills)

    suggestions = get_suggestions(skills)

    return render_template(
        "result.html",
        skills=skills,
        jobs=jobs,
        score=score,
        missing_skills=missing_skills,
        suggestions=suggestions
    )

# -----------------------
# LOGOUT
# -----------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# -----------------------
# RUN
# -----------------------
if __name__ == '__main__':
   import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)