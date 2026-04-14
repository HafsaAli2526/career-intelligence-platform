## career-intelligence-platform
AI-powered career intelligence platform that parses CVs and job descriptions, computes ATS-based match scores, identifies skill gaps, and generates personalized learning recommendations using RAG and NLP techniques.
##
# 🏷️ Badges
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-blue?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?logo=postgresql)
![NLP](https://img.shields.io/badge/NLP-Spacy%20%7C%20Transformers-orange)
![RAG](https://img.shields.io/badge/RAG-LangChain-purple)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

# 🧰 Tech Stack
- 💻 Backend
FastAPI
Python
SQLAlchemy
Pydantic
- 🎨 Frontend
React.js / Next.js
Tailwind CSS
Chart.js / Recharts
- 🧠 AI / NLP
SpaCy
HuggingFace Transformers
Sentence-Transformers (MiniLM/BERT)
Scikit-learn
- 🔍 RAG & Vector Search
LangChain
ChromaDB / FAISS
LLMs (LLaMA / GPT / Claude APIs)
- 🗄️ Database
PostgreSQL (Structured Data)
Vector Database (Embeddings Storage)
- 🌐 Web Scraping
BeautifulSoup
Selenium
Requests
- ⚙️ DevOps / Tools
Git & GitHub
GitHub Actions
Docker (Optional)
- 📌 Key Features
CV Parsing (PDF/DOCX → Structured Data)
Job Description Parsing (with Salary Extraction)
ATS Score Calculation
Semantic CV–JD Matching
Skill Gap Detection
RAG-based Course Recommendations
Interactive Dashboard

## 📋 Features

### Core Functionality
- ✅ **CV Parsing**: Extract job title, skills, experience from PDF/DOCX
- ✅ **JD Parsing**: Parse job descriptions with Pakistani salary extraction
- ✅ **ATS Scoring**: 0-100 score (40% skill + 25% title + 15% exp + 10% edu + 10% tools)
- ✅ **CV-JD Matching**: Semantic (60%) + Skills (30%) + Title (10%)
- ✅ **Skill Gap Analysis**: Categorized missing skills
- ✅ **RAG Recommendations**: AI-powered learning paths
- ✅ **Job Scraping**: Rozee.pk, Indeed.pk, Mustakbil.com

---

## 🏗️ Architecture

```
Frontend (React) → Backend (FastAPI) → Parsers → Data Stores → PostgreSQL + ChromaDB
                                              ↓
                                      Matching + ATS + Skill Gap
                                              ↓
                                      RAG Recommendations
                                              ↓
                                      Dashboard Visualization
```


---

## 📦 Installation

### Quick Setup
```bash
# Run automated setup
python setup.py

# Or manual setup:
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r backend/requirements.txt
python -m spacy download en_core_web_lg
```

### Database Setup
```bash
createdb career_platform
cd backend
python init_db.py
```

### Run Application
```bash
cd backend
uvicorn app.main:app --reload
```

Visit: **http://localhost:8000/docs**

---

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload_cv` | POST | Upload CV file |
| `/parse_jd` | POST | Parse JD text |
| `/scrape_jobs` | POST | Scrape Pakistani job boards |
| `/ats_score` | POST | Compute ATS score (0-100) |
| `/match` | POST | Match CV with all JDs |
| `/skill_gap` | POST | Analyze skill gaps |
| `/recommend` | POST | Get learning recommendations |

---

## 📊 Formulas

### Matching Score
```
final_match_score = 
    (0.6 × semantic_similarity) +
    (0.3 × skill_overlap) +
    (0.1 × title_similarity)
```

### ATS Score
```
ats_score = 
    (0.40 × skill_match) +
    (0.25 × title_alignment) +
    (0.15 × experience_alignment) +
    (0.10 × education_alignment) +
    (0.10 × tools_match)
```

---

## 🎓 FYP Requirements Coverage

| Requirement | Status |
|-------------|--------|
| CV → Data Module | ✅ |
| JD → Data Module | ✅ |
| CV-JD Matching | ✅ |
| ATS Scoring | ✅ |
| Skill Gap Analyzer | ✅ |
| Job Scraper | ✅ |
| RAG Recommendations | ✅ |
| Web Dashboard | ✅ |

---


## 👥 Contributors

- **Hafsa Ali** - FYP 2024

---

**Built with ❤️ for Pakistani Job Market**
