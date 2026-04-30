import os
import re
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
import pdfplumber
import docx

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

# ─── Database Setup ────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect('database/resumes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            candidate_name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            education TEXT,
            experience TEXT,
            linkedin TEXT,
            github TEXT,
            raw_text TEXT,
            uploaded_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ─── Helpers ───────────────────────────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(filepath):
    doc = docx.Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_email(text):
    pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else "Not found"

def extract_phone(text):
    pattern = r'(\+?\d{1,3}[\s\-]?)?(\(?\d{3}\)?[\s\-]?)(\d{3}[\s\-]?\d{4})'
    matches = re.findall(pattern, text)
    if matches:
        full = ''.join([''.join(m) for m in matches[:1]])
        return re.sub(r'\s+', ' ', full).strip()
    return "Not found"

def extract_name(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    # First non-empty line that looks like a name (2-4 words, no special chars except hyphen/period)
    for line in lines[:8]:
        if re.match(r'^[A-Z][a-zA-Z\-\.]+(\s[A-Z][a-zA-Z\-\.]+){1,3}$', line):
            return line
    # Fallback: look for "Name:" pattern
    match = re.search(r'(?i)(?:name\s*[:\-]\s*)([A-Z][a-zA-Z\s]{3,40})', text)
    if match:
        return match.group(1).strip()
    return lines[0] if lines else "Not found"

def extract_linkedin(text):
    match = re.search(r'linkedin\.com/in/([a-zA-Z0-9\-_/]+)', text, re.IGNORECASE)
    return f"linkedin.com/in/{match.group(1)}" if match else "Not found"

def extract_github(text):
    match = re.search(r'github\.com/([a-zA-Z0-9\-_]+)', text, re.IGNORECASE)
    return f"github.com/{match.group(1)}" if match else "Not found"

SKILLS_DB = [
    # Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C", "Go", "Rust",
    "Ruby", "Swift", "Kotlin", "PHP", "R", "MATLAB", "Scala", "Perl", "Shell",
    # Web
    "HTML", "CSS", "React", "Vue", "Angular", "Node.js", "Express", "Django",
    "Flask", "FastAPI", "Spring Boot", "Next.js", "Svelte", "Bootstrap", "Tailwind",
    # Data & ML
    "TensorFlow", "PyTorch", "Keras", "scikit-learn", "Pandas", "NumPy", "Matplotlib",
    "OpenCV", "NLTK", "spaCy", "Transformers", "Hugging Face", "Plotly", "Seaborn",
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Elasticsearch", "Oracle",
    "Cassandra", "Firebase", "DynamoDB", "SQL",
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "GitHub", "GitLab",
    "CI/CD", "Jenkins", "Terraform", "Linux", "Nginx", "Ansible",
    # Other
    "REST API", "GraphQL", "Microservices", "Agile", "Scrum", "Jira", "Figma",
    "Tableau", "Power BI", "Excel", "Streamlit", "Celery", "RabbitMQ", "Kafka"
]

def extract_skills(text):
    found = []
    text_lower = text.lower()
    for skill in SKILLS_DB:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
            if skill not in found:
                found.append(skill)
    return found

def extract_education(text):
    degrees = []
    patterns = [
        r'(?i)(B\.?Tech|Bachelor of Technology|B\.?E\.?|Bachelor of Engineering)',
        r'(?i)(M\.?Tech|Master of Technology|M\.?E\.?|Master of Engineering)',
        r'(?i)(B\.?Sc?\.?|Bachelor of Science)',
        r'(?i)(M\.?Sc?\.?|Master of Science)',
        r'(?i)(MBA|Master of Business Administration)',
        r'(?i)(Ph\.?D\.?|Doctor of Philosophy)',
        r'(?i)(BCA|MCA|B\.?Com|M\.?Com|BA|MA)',
        r'(?i)(Diploma|Certificate|Associate)'
    ]
    for pat in patterns:
        matches = re.findall(pat, text)
        for m in matches:
            if m and m not in degrees:
                degrees.append(m if isinstance(m, str) else m[0])
    return degrees if degrees else ["Not specified"]

def extract_experience(text):
    pattern = r'(?i)(\d+\.?\d*)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:work\s+)?experience'
    match = re.search(pattern, text)
    if match:
        return f"{match.group(1)} years"
    # Check for fresher/entry level
    if re.search(r'(?i)fresher|entry.?level|no experience|0 years', text):
        return "Fresher / Entry Level"
    return "Not specified"

def parse_resume(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        text = extract_text_from_pdf(filepath)
    else:
        text = extract_text_from_docx(filepath)

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "github": extract_github(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "raw_text": text[:3000]
    }

def save_to_db(filename, data):
    conn = sqlite3.connect('database/resumes.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO resumes
        (filename, candidate_name, email, phone, skills, education, experience, linkedin, github, raw_text, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        filename,
        data['name'],
        data['email'],
        data['phone'],
        json.dumps(data['skills']),
        json.dumps(data['education']),
        data['experience'],
        data['linkedin'],
        data['github'],
        data['raw_text'],
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    conn.commit()
    record_id = c.lastrowid
    conn.close()
    return record_id

def get_all_resumes():
    conn = sqlite3.connect('database/resumes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM resumes ORDER BY uploaded_at DESC')
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            "id": row[0], "filename": row[1], "name": row[2],
            "email": row[3], "phone": row[4],
            "skills": json.loads(row[5]) if row[5] else [],
            "education": json.loads(row[6]) if row[6] else [],
            "experience": row[7], "linkedin": row[8], "github": row[9],
            "uploaded_at": row[11]
        })
    return result

def search_resumes(query):
    conn = sqlite3.connect('database/resumes.db')
    c = conn.cursor()
    q = f"%{query}%"
    c.execute('''
        SELECT * FROM resumes
        WHERE candidate_name LIKE ? OR email LIKE ? OR skills LIKE ? OR education LIKE ?
        ORDER BY uploaded_at DESC
    ''', (q, q, q, q))
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            "id": row[0], "filename": row[1], "name": row[2],
            "email": row[3], "phone": row[4],
            "skills": json.loads(row[5]) if row[5] else [],
            "education": json.loads(row[6]) if row[6] else [],
            "experience": row[7], "linkedin": row[8], "github": row[9],
            "uploaded_at": row[11]
        })
    return result

# ─── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF and DOCX files are allowed'}), 400

    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        parsed = parse_resume(filepath)
        record_id = save_to_db(filename, parsed)
        parsed['id'] = record_id
        return jsonify({'success': True, 'data': parsed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/resumes', methods=['GET'])
def list_resumes():
    query = request.args.get('search', '')
    if query:
        data = search_resumes(query)
    else:
        data = get_all_resumes()
    return jsonify(data)

@app.route('/resumes/<int:resume_id>', methods=['DELETE'])
def delete_resume(resume_id):
    conn = sqlite3.connect('database/resumes.db')
    c = conn.cursor()
    c.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('database', exist_ok=True)
    init_db()
    app.run(debug=True, port=5000)
