from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.jd import JDData
from app.schemas.jd_schema import JDParseRequest, JDResponse, JDListResponse
from app.services.jd_parser import JDParser

router = APIRouter(prefix="/api/jd", tags=["Job Description Management"])

# Initialize parser
jd_parser = JDParser()


@router.post("/parse", response_model=JDResponse)
async def parse_jd(request: JDParseRequest, db: Session = Depends(get_db)):
    """
    Parse job description from text
    """
    try:
        # Parse JD
        jd_data = jd_parser.parse_jd(
            request.jd_text,
            source_url=request.source_url,
            source_platform=request.source_platform
        )
        
        # Extract salary info
        salary_info = jd_data.get('salary_info', {})
        
        # Save to database
        jd_record = JDData(
            job_title=jd_data.get('job_title'),
            company=jd_data.get('company'),
            location=jd_data.get('location'),
            salary_min=salary_info.get('min'),
            salary_max=salary_info.get('max'),
            salary_currency=salary_info.get('currency', 'PKR'),
            salary_text=salary_info.get('text'),
            required_skills=jd_data.get('required_skills', []),
            soft_skills=jd_data.get('soft_skills', []),
            responsibilities=jd_data.get('responsibilities', []),
            experience_required=jd_data.get('experience_required'),
            education_required=jd_data.get('education_required'),
            work_type=jd_data.get('work_type'),
            employment_type=jd_data.get('employment_type'),
            raw_text=request.jd_text,
            source_url=request.source_url,
            source_platform=request.source_platform,
            embedding=jd_data.get('embedding')
        )
        
        db.add(jd_record)
        db.commit()
        db.refresh(jd_record)
        
        return jd_record
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{jd_id}", response_model=JDResponse)
async def get_jd(jd_id: int, db: Session = Depends(get_db)):
    """Get JD by ID"""
    jd = db.query(JDData).filter(JDData.id == jd_id).first()
    
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    return jd


@router.get("/", response_model=JDListResponse)
async def list_jds(
    skip: int = 0,
    limit: int = 50,
    location: str = None,
    db: Session = Depends(get_db)
):
    """List all JDs with pagination and optional filtering"""
    query = db.query(JDData)
    
    if location:
        query = query.filter(JDData.location.ilike(f"%{location}%"))
    
    jds = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return JDListResponse(total=total, jds=jds)


@router.delete("/{jd_id}")
async def delete_jd(jd_id: int, db: Session = Depends(get_db)):
    """Delete JD by ID"""
    jd = db.query(JDData).filter(JDData.id == jd_id).first()
    
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    db.delete(jd)
    db.commit()
    
    return {"message": "Job description deleted successfully", "jd_id": jd_id}


