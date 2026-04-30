# 📄 ResumeIQ — Automated Resume Parser

An intelligent resume parsing system built with Python and Flask that extracts key candidate information from PDF and DOCX resumes and stores it in a searchable SQLite database.

---

## 🚀 Features

- **Multi-format Support**: Parse PDF (via pdfplumber) and DOCX (via python-docx) resumes
- **Smart Extraction**: Automatically extracts:
  - Candidate Name, Email, Phone
  - LinkedIn & GitHub profiles
  - 50+ technical skills across languages, frameworks, and databases
  - Education degrees and qualifications
  - Years of experience
- **SQLite Database**: All parsed candidates stored in a structured, searchable DB
- **Search**: Filter candidates by name, skill, or email instantly
- **Modern UI**: Drag-and-drop upload, real-time results, beautiful dark interface

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| NLP/Extraction | Regex-based (no external API needed) |
| Database | SQLite |
| Frontend | Vanilla HTML/CSS/JS |

---

## 📦 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/resume-parser.git
cd resume-parser
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

### 5. Open your browser
```
http://localhost:5000
```

---

## 📁 Project Structure

```
resume_parser/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md
├── templates/
│   └── index.html          # Frontend UI
├── uploads/                # Uploaded resume files (auto-created)
└── database/
    └── resumes.db          # SQLite database (auto-created)
```

---

## 🧠 How It Works

1. User uploads a resume (PDF or DOCX) via drag-and-drop
2. `pdfplumber` or `python-docx` extracts raw text
3. Regex patterns extract structured fields (email, phone, name, etc.)
4. 50+ skill keywords are matched against extracted text
5. Results saved to SQLite via Python's built-in `sqlite3`
6. UI displays parsed data and updates the candidate database

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload and parse a resume |
| `GET` | `/resumes` | List all parsed resumes |
| `GET` | `/resumes?search=python` | Search candidates |
| `DELETE` | `/resumes/<id>` | Delete a candidate |

---

## 📸 Screenshots

> Upload a PDF → Instantly see extracted Name, Email, Skills, Education

---

## 🤝 Contributing

Pull requests welcome! For major changes, open an issue first.

---

## 📝 License

MIT License — free for personal and commercial use.

---

*Built as part of the 1-Month Python Developer Internship at Codec Technologies*
