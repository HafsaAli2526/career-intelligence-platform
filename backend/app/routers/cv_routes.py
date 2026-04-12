from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path

from app.database import get_db
from app.models.cv import CVData
from app.schemas.cv_schema import CVUploadResponse, CVResponse, CVListResponse
from app.services.cv_parser import CVParser

router = APIRouter(prefix="/api/cv", tags=["CV Management"])

# Initialize parser
cv_parser = CVParser()

# Upload directory
UPLOAD_DIR = Path("uploads/cvs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=CVUploadResponse)
async def upload_cv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and parse CV
    Supports: PDF, DOCX
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.docx')):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are supported"
            )
        
        # Save file temporarily
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse CV
        cv_data = cv_parser.parse_cv(str(file_path))
        
        # Save to database
        cv_record = CVData(
            full_name=cv_data.get('full_name'),
            email=cv_data.get('email'),
            phone=cv_data.get('phone'),
            linkedin_url=cv_data.get('linkedin_url'),
            github_url=cv_data.get('github_url'),
            job_title=cv_data.get('job_title'),
            career_objective=cv_data.get('career_objective'),
            skills=cv_data.get('skills', []),
            education=cv_data.get('education', []),
            experience=cv_data.get('experience', []),
            projects=cv_data.get('projects', []),
            certifications=cv_data.get('certifications', []),
            summary=cv_data.get('summary'),
            raw_text=cv_data.get('raw_text'),
            embedding=cv_data.get('embedding')
        )
        
        db.add(cv_record)
        db.commit()
        db.refresh(cv_record)
        
        # Clean up file (optional - keep if you want to store CVs)
        # os.remove(file_path)
        
        return CVUploadResponse(
            message="CV uploaded and parsed successfully",
            cv_id=cv_record.id,
            data=cv_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cv_id}", response_model=CVResponse)
async def get_cv(cv_id: int, db: Session = Depends(get_db)):
    """Get CV by ID"""
    cv = db.query(CVData).filter(CVData.id == cv_id).first()
    
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    
    return cv


@router.get("/", response_model=CVListResponse)
async def list_cvs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all CVs with pagination"""
    cvs = db.query(CVData).offset(skip).limit(limit).all()
    total = db.query(CVData).count()
    
    return CVListResponse(total=total, cvs=cvs)


@router.delete("/{cv_id}")
async def delete_cv(cv_id: int, db: Session = Depends(get_db)):
    """Delete CV by ID"""
    cv = db.query(CVData).filter(CVData.id == cv_id).first()
    
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    
    db.delete(cv)
    db.commit()
    
    return {"message": "CV deleted successfully", "cv_id": cv_id}