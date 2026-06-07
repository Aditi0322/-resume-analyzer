import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from flask import Flask, render_template, request
from parser import extract_text, extract_skills, recommend_jobs, get_ai_feedback, get_missing_skills, get_resume_score

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["resume"]

    if file.filename == "":
        return render_template("index.html", error="No file selected!")

    temp_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(temp_path)

    resume_text = extract_text(temp_path)

    if "Error" in resume_text:
        return render_template("index.html", error=resume_text)

    skills = extract_skills(resume_text)
    recommendations = recommend_jobs(resume_text)
    top_career = recommendations[0][0]
    ai_feedback = get_ai_feedback(resume_text, top_career)
    missing_skills = get_missing_skills(top_career, skills)
    resume_score = get_resume_score(skills, recommendations)

    return render_template("index.html",
                           skills=skills,
                           recommendations=recommendations,
                           ai_feedback=ai_feedback,
                           missing_skills=missing_skills,
                           resume_score=resume_score)

if __name__ == "__main__":
    app.run(debug=True)