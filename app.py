import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
from parser import extract_text, extract_skills, recommend_jobs, get_ai_feedback, get_missing_skills, get_resume_score

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==============================
# DATABASE MODELS
# ==============================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    results = db.relationship('Result', backref='user', lazy=True)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(100))
    top_career = db.Column(db.String(100))
    score = db.Column(db.Integer)
    skills = db.Column(db.String(500))
    date = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==============================
# ROUTES
# ==============================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return redirect(url_for('register'))

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    results = Result.query.filter_by(user_id=current_user.id).order_by(Result.date.desc()).all()
    return render_template('dashboard.html', results=results)

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    file = request.files['resume']

    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('home'))

    temp_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(temp_path)

    resume_text = extract_text(temp_path)

    if 'Error' in resume_text:
        flash(resume_text, 'error')
        return redirect(url_for('home'))

    skills = extract_skills(resume_text)
    recommendations = recommend_jobs(resume_text)
    top_career = recommendations[0][0]
    ai_feedback = get_ai_feedback(resume_text, top_career)
    missing_skills = get_missing_skills(top_career, skills)
    resume_score = get_resume_score(skills, recommendations)

    # Save to database
    result = Result(
        user_id=current_user.id,
        filename=file.filename,
        top_career=top_career,
        score=resume_score,
        skills=', '.join(skills)
    )
    db.session.add(result)
    db.session.commit()

    return render_template('index.html',
                           skills=skills,
                           recommendations=recommendations,
                           ai_feedback=ai_feedback,
                           missing_skills=missing_skills,
                           resume_score=resume_score)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
