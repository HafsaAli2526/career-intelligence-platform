from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cv import CVData
from app.models.jd import JDData
from app.models.match import Match
from app.models.skill_gap import SkillGap
from app.schemas.match_schema import MatchResponse, SkillGapResponse, RecommendationResponse
from app.services.matcher import JobMatcher
from app.services.skill_gap import SkillGapAnalyzer
from app.services.rag_engine import RAGRecommendationEngine

router = APIRouter(prefix="/api", tags=["Matching & Recommendations"])

# Initialize services
matcher = JobMatcher()
skill_gap_analyzer = SkillGapAnalyzer()
rag_engine = RAGRecommendationEngine()


@router.post("/match/{cv_id}", response_model=MatchResponse)
async def match_cv(cv_id: int, top_k: int = 10, db: Session = Depends(get_db)):
    """
    Match CV against all available JDs
    Returns top K matches sorted by score
    """
    # Get CV
    cv = db.query(CVData).filter(CVData.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    
    # Get all JDs
    jds = db.query(JDData).all()
    
    if not jds:
        raise HTTPException(status_code=404, detail="No job descriptions available")
    
    # Convert to dict format for matcher
    cv_data = {
        'job_title': cv.job_title,
        'skills': cv.skills,
        'embedding': cv.embedding
    }
    
    jd_list = []
    for jd in jds:
        jd_list.append({
            'id': jd.id,
            'job_title': jd.job_title,
            'company': jd.company,
            'location': jd.location,
            'required_skills': jd.required_skills,
            'soft_skills': jd.soft_skills,
            'embedding': jd.embedding,
            'salary_info': {
                'min': jd.salary_min,
                'max': jd.salary_max,
                'currency': jd.salary_currency,
                'text': jd.salary_text
            }
        })
    
    # Perform matching
    matches = matcher.match_cv_with_jds(cv_data, jd_list, top_k)
    
    # Save matches to database
    for match in matches:
        match_record = Match(
            cv_id=cv_id,
            jd_id=match['jd_id'],
            semantic_score=match['semantic_score'],
            skill_overlap_score=match['skill_overlap_score'],
            title_match_score=match['title_match_score'],
            final_score=match['final_score'],
            rank=match['rank']
        )
        db.add(match_record)
    
    db.commit()
    
    return MatchResponse(
        cv_id=cv_id,
        total_jobs_analyzed=len(jds),
        top_matches=matches
    )


@router.get("/matches/{cv_id}")
async def get_matches(cv_id: int, db: Session = Depends(get_db)):
    """Get saved matches for a CV"""
    matches = db.query(Match)\
        .filter(Match.cv_id == cv_id)\
        .order_by(Match.final_score.desc())\
        .all()
    
    if not matches:
        raise HTTPException(
            status_code=404,
            detail="No matches found. Run matching first."
        )
    
    return matches


@router.post("/skill-gap/{cv_id}/{jd_id}", response_model=SkillGapResponse)
async def analyze_skill_gap(cv_id: int, jd_id: int, db: Session = Depends(get_db)):
    """
    Analyze skill gap between CV and specific JD
    """
    # Get CV and JD
    cv = db.query(CVData).filter(CVData.id == cv_id).first()
    jd = db.query(JDData).filter(JDData.id == jd_id).first()
    
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Prepare data
    cv_data = {
        'skills': cv.skills,
        'job_title': cv.job_title
    }
    
    jd_data = {
        'required_skills': jd.required_skills,
        'soft_skills': jd.soft_skills,
        'job_title': jd.job_title
    }
    
    # Analyze gap
    gap_analysis = skill_gap_analyzer.analyze_gap(cv_data, jd_data)
    
    # Save to database
    gap_record = SkillGap(
        cv_id=cv_id,
        jd_id=jd_id,
        missing_technical_skills=gap_analysis['missing_technical_skills'],
        missing_soft_skills=gap_analysis['missing_soft_skills']
    )
    
    db.add(gap_record)
    db.commit()
    
    return SkillGapResponse(
        cv_id=cv_id,
        jd_id=jd_id,
        **gap_analysis
    )


@router.post("/recommend/{cv_id}/{jd_id}", response_model=RecommendationResponse)
async def get_recommendations(cv_id: int, jd_id: int, db: Session = Depends(get_db)):
    """
    Generate personalized learning recommendations using RAG
    """
    # First get skill gap
    cv = db.query(CVData).filter(CVData.id == cv_id).first()
    jd = db.query(JDData).filter(JDData.id == jd_id).first()
    
    if not cv or not jd:
        raise HTTPException(status_code=404, detail="CV or JD not found")
    
    # Get skill gap
    cv_data = {'skills': cv.skills, 'job_title': cv.job_title}
    jd_data = {
        'required_skills': jd.required_skills,
        'soft_skills': jd.soft_skills,
        'job_title': jd.job_title
    }
    
    gap_analysis = skill_gap_analyzer.analyze_gap(cv_data, jd_data)
    missing_skills = gap_analysis['missing_technical_skills']
    
    if not missing_skills:
        return RecommendationResponse(
            recommendations=[],
            courses=[],
            missing_skills=[],
            roadmap="No skill gaps found! You're a great match for this position.",
            metadata={'skill_count': 0, 'courses_found': 0}
        )
    
    # Generate recommendations using RAG
    recommendations = rag_engine.generate_recommendations(
        missing_skills,
        cv_data,
        jd_data
    )
    
    return recommendations