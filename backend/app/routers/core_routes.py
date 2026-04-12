from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pathlib import Path
import shutil

from app.database import get_db
from app.services.cv_parser import CVParser
from app.services.jd_parser import JDParser
from app.services.matcher import JobMatcher
from app.services.ats_scorer import ATSScorer
from app.services.skill_gap import SkillGapAnalyzer
from app.services.rag_engine import RAGRecommendationEngine
from app.services.data_store import CVDataStore, JDDataStore, ResultsDataStore
from app.services.scraper import UnifiedJobScraper
from app.config import settings

router = APIRouter(tags=["Core API"])

# Initialize services
cv_parser = CVParser()
jd_parser = JDParser()
matcher = JobMatcher()
ats_scorer = ATSScorer()
skill_gap_analyzer = SkillGapAnalyzer()
rag_engine = RAGRecommendationEngine()
job_scraper = UnifiedJobScraper()

# Upload directory
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload_cv")
async def upload_cv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and parse CV (PDF/DOCX)"""
    try:
        if not file.filename.endswith(tuple(settings.ALLOWED_EXTENSIONS)):
            raise HTTPException(400, "Only PDF and DOCX files supported")
        
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse CV
        parsed_cv_data = cv_parser.parse_cv(str(file_path))
        
        # Store in database
        cv_data_store = CVDataStore(db)
        cv_id = cv_data_store.store_cv(parsed_cv_data)
        
        return {
            "status": "success",
            "message": "CV uploaded and parsed successfully",
            "cv_id": cv_id,
            "parsed_data": {
                "full_name": parsed_cv_data.get('full_name'),
                "email": parsed_cv_data.get('email'),
                "job_title": parsed_cv_data.get('job_title'),
                "skills": parsed_cv_data.get('skills', [])
            }
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/parse_cv")
async def parse_cv_text(cv_text: str, db: Session = Depends(get_db)):
    """Parse CV from text"""
    try:
        temp_path = UPLOAD_DIR / "temp_cv.txt"
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(cv_text)
        
        parsed_cv_data = cv_parser.parse_cv(str(temp_path))
        cv_data_store = CVDataStore(db)
        cv_id = cv_data_store.store_cv(parsed_cv_data)
        
        temp_path.unlink()
        
        return {"status": "success", "cv_id": cv_id}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/parse_jd")
async def parse_jd_manual(jd_text: str, db: Session = Depends(get_db)):
    """Parse JD from text"""
    try:
        parsed_jd = jd_parser.parse_jd(jd_text, source_platform="manual")
        jd_data_store = JDDataStore(db)
        jd_id = jd_data_store.store_jd(parsed_jd)
        
        return {
            "status": "success",
            "jd_id": jd_id,
            "parsed_data": {
                "job_title": parsed_jd.get('job_title'),
                "company": parsed_jd.get('company'),
                "salary_info": parsed_jd.get('salary_info')
            }
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/scrape_jobs")
async def scrape_jobs(
    background_tasks: BackgroundTasks,
    keyword: str = "python developer",
    location: str = "karachi",
    pages: int = 2,
    db: Session = Depends(get_db)
):
    """Scrape jobs (Rozee, Indeed, Mustakbil)"""
    
    def scrape_and_store():
        try:
            raw_jobs = job_scraper.scrape_all(keyword, location, pages)
            jd_data_store = JDDataStore(db)
            
            for job in raw_jobs:
                parsed_jd = jd_parser.parse_jd(
                    job.get('raw_text', ''),
                    source_url=job.get('source_url'),
                    source_platform=job.get('source_platform')
                )
                jd_data_store.store_jd(parsed_jd)
        except Exception as e:
            print(f"Scraping error: {e}")
    
    background_tasks.add_task(scrape_and_store)
    
    return {
        "status": "processing",
        "message": "Job scraping started",
        "parameters": {"keyword": keyword, "location": location, "pages": pages}
    }


@router.post("/ats_score")
async def compute_ats_score(cv_id: int, jd_id: int, db: Session = Depends(get_db)):
    """Compute ATS score (0-100)"""
    try:
        cv_data_store = CVDataStore(db)
        jd_data_store = JDDataStore(db)
        
        cv_data = cv_data_store.get_cv(cv_id)
        jd_data = jd_data_store.get_jd(jd_id)
        
        if not cv_data or not jd_data:
            raise HTTPException(404, "CV or JD not found")
        
        ats_result = ats_scorer.compute_ats_score(cv_data, jd_data)
        
        results_store = ResultsDataStore(db)
        ats_score_id = results_store.store_ats_score(cv_id, jd_id, ats_result)
        
        return {"status": "success", "ats_score_id": ats_score_id, "result": ats_result}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/match")
async def match_cv_with_jds(cv_id: int, top_k: int = 10, db: Session = Depends(get_db)):
    """Match CV with all JDs"""
    try:
        cv_data_store = CVDataStore(db)
        jd_data_store = JDDataStore(db)
        
        cv_data = cv_data_store.get_cv(cv_id)
        all_jds = jd_data_store.get_all_jds()
        
        if not cv_data or not all_jds:
            raise HTTPException(404, "CV or JDs not found")
        
        matches = matcher.match_cv_with_jds(cv_data, all_jds, top_k)
        
        results_store = ResultsDataStore(db)
        for match in matches:
            results_store.store_match(cv_id, match['jd_id'], match)
        
        return {
            "status": "success",
            "cv_id": cv_id,
            "total_jobs_analyzed": len(all_jds),
            "top_matches": matches
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/skill_gap")
async def analyze_skill_gap(cv_id: int, jd_id: int, db: Session = Depends(get_db)):
    """Analyze skill gaps"""
    try:
        cv_data_store = CVDataStore(db)
        jd_data_store = JDDataStore(db)
        
        cv_data = cv_data_store.get_cv(cv_id)
        jd_data = jd_data_store.get_jd(jd_id)
        
        if not cv_data or not jd_data:
            raise HTTPException(404, "CV or JD not found")
        
        gap_result = skill_gap_analyzer.analyze_gap(cv_data, jd_data)
        
        results_store = ResultsDataStore(db)
        gap_id = results_store.store_skill_gap(cv_id, jd_id, gap_result)
        
        return {"status": "success", "gap_id": gap_id, "result": gap_result}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/recommend")
async def get_recommendations(cv_id: int, jd_id: int, db: Session = Depends(get_db)):
    """Get RAG-based recommendations"""
    try:
        cv_data_store = CVDataStore(db)
        jd_data_store = JDDataStore(db)
        
        cv_data = cv_data_store.get_cv(cv_id)
        jd_data = jd_data_store.get_jd(jd_id)
        
        gap_result = skill_gap_analyzer.analyze_gap(cv_data, jd_data)
        missing_skills = gap_result['missing_technical_skills']
        
        if not missing_skills:
            return {"status": "success", "message": "No gaps!", "recommendations": []}
        
        recommendations = rag_engine.generate_recommendations(missing_skills, cv_data, jd_data)
        
        return {"status": "success", "recommendations": recommendations}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/cv/{cv_id}")
async def get_cv(cv_id: int, db: Session = Depends(get_db)):
    """Get CV by ID"""
    cv_data_store = CVDataStore(db)
    cv_data = cv_data_store.get_cv(cv_id)
    
    if not cv_data:
        raise HTTPException(404, "CV not found")
    
    return {"status": "success", "cv": cv_data}


@router.get("/jd/{jd_id}")
async def get_jd(jd_id: int, db: Session = Depends(get_db)):
    """Get JD by ID"""
    jd_data_store = JDDataStore(db)
    jd_data = jd_data_store.get_jd(jd_id)
    
    if not jd_data:
        raise HTTPException(404, "JD not found")
    
    return {"status": "success", "jd": jd_data}


@router.get("/matches/{cv_id}")
async def get_matches(cv_id: int, db: Session = Depends(get_db)):
    """Get matches for CV"""
    from app.models.match import Match
    
    matches = db.query(Match)\
        .filter(Match.cv_id == cv_id)\
        .order_by(Match.final_score.desc())\
        .all()
    
    if not matches:
        raise HTTPException(404, "No matches found")
    
    return {
        "status": "success",
        "cv_id": cv_id,
        "matches": [
            {
                "jd_id": m.jd_id,
                "final_score": m.final_score,
                "rank": m.rank
            }
            for m in matches
        ]
    }

