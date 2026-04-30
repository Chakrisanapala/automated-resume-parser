# 📄 ResumeIQ — Automated Resume Parser

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat)

An intelligent resume parsing system built with Python and Flask that extracts key candidate information from PDF and DOCX resumes and stores results in a searchable SQLite database — no external NLP API required.

---

## ✨ Features

- **Multi-format Support** — Parse both PDF (`pdfplumber`) and DOCX (`python-docx`) resumes
- **Smart Extraction** — Automatically identifies:
  - Candidate name, email, and phone number
  - LinkedIn and GitHub profile URLs
  - 80+ technical skills across languages, frameworks, databases, and cloud tools
  - Degree and education qualifications
  - Years of experience
- **SQLite Database** — All parsed candidates stored in a structured, queryable local DB
- **Full-Text Search** — Filter candidates by name, skill, email, or education instantly
- **Modern Dark UI** — Drag-and-drop upload, animated progress, live result cards

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+, Flask 3.0 |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| NLP / Extraction | Regex-based (no external API) |
| Database | SQLite (built-in) |
| Frontend | Vanilla HTML / CSS / JS |

---

## 📁 Project Structure

```
resume_parser/
├── app.py                  # Flask app — routes, parsing logic, DB helpers
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .gitignore
├── templates/
│   └── index.html          # Full frontend UI (drag-drop, results, table)
├── uploads/                # Uploaded resume files (auto-created on first run)
└── database/
    └── resumes.db          # SQLite database (auto-created on first run)
```

---

## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/resume-parser.git
cd resume-parser
```

### 2. Create & activate a virtual environment
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

### 5. Open in your browser
```
http://localhost:5000
```

The `uploads/` and `database/` folders are created automatically on first run.

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve the main UI |
| `POST` | `/upload` | Upload and parse a resume file |
| `GET` | `/resumes` | List all parsed candidates |
| `GET` | `/resumes?search=python` | Search candidates by keyword |
| `DELETE` | `/resumes/<id>` | Remove a candidate record |

### Example — Upload a resume
```bash
curl -X POST http://localhost:5000/upload \
     -F "file=@john_doe_resume.pdf"
```

### Example — Search by skill
```bash
curl http://localhost:5000/resumes?search=React
```

---

## 🧠 How It Works

```
PDF / DOCX file
      │
      ▼
 Text Extraction          ← pdfplumber / python-docx
      │
      ▼
 Regex Extractors         ← name, email, phone, LinkedIn, GitHub
      │
      ▼
 Skill Matcher            ← 80+ keyword patterns
      │
      ▼
 SQLite Storage           ← sqlite3 (built-in, no server needed)
      │
      ▼
 JSON API Response        ← displayed in the browser UI
```

---

## ⚠️ Notes

- Resume parsing accuracy depends on formatting; clean, ATS-friendly PDFs yield the best results.
- The `uploads/` folder is included in `.gitignore` to avoid committing personal resume files.
- Not intended for production use without authentication — add Flask-Login or an API key guard before deploying publicly.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## 📝 License

MIT License — free for personal and commercial use.

---

*Built as part of the 1-Month Python Developer Internship at Codec Technologies*
