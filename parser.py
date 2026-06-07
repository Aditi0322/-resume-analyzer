import os
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# ==============================
# STEP 1: EXTRACT TEXT FROM PDF
# ==============================

def extract_text(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
        return text.strip()
    except FileNotFoundError:
        return "Error: File not found. Check file name/path."
    except Exception as e:
        return f"Error: {e}"


# ==============================
# STEP 2: SKILL EXTRACTION
# ==============================

skills_list = [
    "python", "java", "c++", "machine learning",
    "data science", "react", "nodejs", "docker",
    "sql", "javascript", "html", "css", "api",
    "aws", "linux", "kubernetes"
]

def extract_skills(text):
    found_skills = []
    text = text.lower()
    for skill in skills_list:
        if skill in text:
            found_skills.append(skill)
    return found_skills


# ==============================
# STEP 3: JOB RECOMMENDATION
# ==============================

def recommend_jobs(resume_text):
    jobs = {
        "Data Scientist": "python machine learning data analysis statistics pandas numpy",
        "Web Developer": "html css javascript react nodejs frontend backend web",
        "Software Engineer": "java c++ python algorithms data structures problem solving",
        "AI Engineer": "machine learning deep learning python neural networks tensorflow",
        "DevOps Engineer": "docker kubernetes ci cd cloud aws linux automation",
        "Data Analyst": "excel sql power bi data visualization statistics python",
        "Cyber Security": "network security ethical hacking penetration testing kali linux"
    }

    job_titles = list(jobs.keys())
    job_desc = list(jobs.values())
    documents = [resume_text] + job_desc

    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(vectors[0:1], vectors[1:])[0]
    top_indices = similarity.argsort()[-3:][::-1]

    return [(job_titles[i], round(similarity[i], 2)) for i in top_indices]


# ==============================
# STEP 4: AI FEEDBACK
# ==============================

def get_ai_feedback(resume_text, top_career):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = (
            "You are a career counselor. Analyze this resume and give advice. "
            "Top career match: " + top_career + ". "
            "Resume: " + resume_text[:1000] + ". "
            "Give 3-4 sentences of friendly specific career advice. "
            "Mention strengths and what to improve."
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Could not generate feedback: {e}"
    
    # ==============================
# STEP 5: MISSING SKILLS
# ==============================

def get_missing_skills(top_career, found_skills):
    career_skills = {
        "Web Developer": ["html", "css", "javascript", "react", "nodejs", "api"],
        "Data Scientist": ["python", "machine learning", "pandas", "numpy", "sql", "tensorflow"],
        "Software Engineer": ["java", "c++", "python", "algorithms", "docker", "api"],
        "AI Engineer": ["python", "tensorflow", "machine learning", "deep learning", "numpy"],
        "DevOps Engineer": ["docker", "kubernetes", "aws", "linux", "sql", "api"],
        "Data Analyst": ["sql", "python", "javascript", "html", "css", "api"],
        "Cyber Security": ["linux", "python", "sql", "api", "docker", "aws"]
    }
    required = career_skills.get(top_career, [])
    missing = [s for s in required if s not in found_skills]
    return missing


# ==============================
# STEP 6: RESUME SCORE
# ==============================

def get_resume_score(found_skills, recommendations):
    skill_score = min(len(found_skills) * 10, 50)
    top_match_score = int(recommendations[0][1] * 100)
    match_score = min(top_match_score * 2, 50)
    total = skill_score + match_score
    return min(total, 100)