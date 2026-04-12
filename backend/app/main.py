
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.database import engine, Base
from app.routers import core_router
from app.config import settings

# Setup logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
logger.info("Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables created")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## AI-Powered Career Intelligence Platform
    
    ### Features
    - **CV Parsing**: Extract job title, skills, experience from PDF/DOCX
    - **JD Parsing**: Parse job descriptions with salary extraction (Pakistani formats)
    - **ATS Scoring**: 0-100 score (40% skill + 25% title + 15% exp + 10% edu + 10% tools)
    - **CV-JD Matching**: Semantic (60%) + Skills (30%) + Title (10%)
    - **Skill Gap Analysis**: Identify missing skills with categorization
    - **RAG Recommendations**: AI-powered learning paths (Coursera, DigiSkills, YouTube)
    - **Job Scraping**: Rozee.pk, Indeed.pk, Mustakbil.com
    
    ### Architecture Flow
    ```
    CV Upload → Parser → Data Store → PostgreSQL + Vector DB
                                    ↓
                            Matching + ATS + Skill Gap
                                    ↓
                            RAG Recommendations
                                    ↓
                            Dashboard Visualization
    ```
    
    ### Tech Stack
    - **Backend**: FastAPI, SQLAlchemy, Pydantic
    - **Database**: PostgreSQL, ChromaDB (Vector Store)
    - **NLP**: SpaCy, Sentence-BERT (MiniLM)
    - **RAG**: LangChain + GPT-4/Claude
    - **Scraping**: BeautifulSoup, Selenium
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(core_router)

# Root endpoint
@app.get("/")
async def root():
    """API Root - System Information"""
    return {
        "project": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "description": "CV-JD Parsing, ATS Scoring, Matching Engine, Skill Gap Analyzer & RAG Recommendation System",
        "docs": "/docs",
        "endpoints": {
            "cv_upload": "POST /upload_cv - Upload CV file",
            "cv_parse": "POST /parse_cv - Parse CV from text",
            "jd_parse": "POST /parse_jd - Parse JD from text",
            "job_scraping": "POST /scrape_jobs - Scrape Pakistani job boards",
            "ats_scoring": "POST /ats_score - Compute ATS score (0-100)",
            "matching": "POST /match - Match CV with all JDs",
            "skill_gap": "POST /skill_gap - Analyze skill gaps",
            "recommendations": "POST /recommend - RAG-based recommendations",
            "get_cv": "GET /cv/{id} - Retrieve CV",
            "get_jd": "GET /jd/{id} - Retrieve JD",
            "get_matches": "GET /matches/{cv_id} - Get job matches"
        },
        "architecture": {
            "frontend": "React.js / Next.js",
            "backend": "FastAPI",
            "database": "PostgreSQL + ChromaDB",
            "nlp": "SpaCy + Sentence-BERT",
            "rag": "LangChain + GPT/Claude/Llama",
            "scrapers": ["Rozee.pk", "Indeed.pk", "Mustakbil.com"]
        },
        "formulas": {
            "matching": "0.6 × semantic + 0.3 × skills + 0.1 × title",
            "ats_score": "40% skill + 25% title + 15% exp + 10% edu + 10% tools"
        }
    }


# Health check
@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "cv_parser": "operational",
            "jd_parser": "operational",
            "ats_scorer": "operational",
            "matcher": "operational",
            "skill_gap_analyzer": "operational",
            "rag_engine": "operational",
            "job_scraper": "operational"
        }
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("=" * 70)
    logger.info(f"🚀 Starting {settings.APP_NAME}")
    logger.info("=" * 70)
    logger.info("✓ Database: Connected")
    logger.info("✓ NLP Models: Loaded")
    logger.info("✓ API Routes: Registered")
    logger.info("✓ Vector Store: Ready")
    logger.info("=" * 70)
    logger.info(f"📚 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 70)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Career Intelligence Platform...")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )


# ============================================================================
# USAGE EXAMPLES IN COMMENTS
# ============================================================================

"""
## Complete Workflow Example

### 1. Upload CV
curl -X POST "http://localhost:8000/upload_cv" \\
  -F "file=@my_cv.pdf"

Response:
{
  "status": "success",
  "cv_id": 1,
  "parsed_data": {
    "full_name": "John Doe",
    "job_title": "Python Developer",
    "skills": ["python", "django", "postgresql"]
  }
}

### 2. Scrape Jobs
curl -X POST "http://localhost:8000/scrape_jobs?keyword=python&location=karachi&pages=2"

Response:
{
  "status": "processing",
  "message": "Job scraping started"
}

### 3. Compute ATS Score (NEW)
curl -X POST "http://localhost:8000/ats_score?cv_id=1&jd_id=5"

Response:
{
  "status": "success",
  "result": {
    "ats_score": 82.7,
    "common_skills": ["python", "django"],
    "missing_skills": ["fastapi", "redis"],
    "breakdown": {
      "skill_match": "85.0% (weight: 40%)",
      "title_alignment": "89.5% (weight: 25%)",
      "experience_alignment": "100.0% (weight: 15%)",
      "education_alignment": "100.0% (weight: 10%)",
      "tools_match": "75.0% (weight: 10%)"
    }
  }
}

### 4. Match CV with All Jobs
curl -X POST "http://localhost:8000/match?cv_id=1&top_k=10"

Response:
{
  "status": "success",
  "top_matches": [
    {
      "rank": 1,
      "jd_title": "Senior Python Developer",
      "final_score": 0.87,
      "semantic_score": 0.89,
      "skill_overlap_score": 0.85
    }
  ]
}

### 5. Skill Gap Analysis
curl -X POST "http://localhost:8000/skill_gap?cv_id=1&jd_id=5"

Response:
{
  "status": "success",
  "result": {
    "missing_technical_skills": ["fastapi", "redis", "aws"],
    "gap_severity": "medium",
    "match_percentage": 75.5
  }
}

### 6. Get RAG Recommendations
curl -X POST "http://localhost:8000/recommend?cv_id=1&jd_id=5"

Response:
{
  "status": "success",
  "recommendations": {
    "courses": [
      {
        "skill": "FastAPI",
        "course_title": "FastAPI Complete Course",
        "provider": "Udemy"
      }
    ],
    "roadmap": "Start with FastAPI basics..."
  }
}
"""