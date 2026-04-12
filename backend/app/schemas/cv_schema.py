from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime

class CVBase(BaseModel):
    """Base CV schema"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    job_title: Optional[str] = None  # Career objective
    career_objective: Optional[str] = None
    skills: List[str] = []
    education: List[Dict] = []
    experience: List[Dict] = []
    projects: List[Dict] = []
    certifications: List[str] = []
    summary: Optional[str] = None

class CVUploadResponse(BaseModel):
    """Response after CV upload"""
    status: str
    message: str
    cv_id: int
    parsed_data: Dict

    class Config:
        from_attributes = True

class CVResponse(BaseModel):
    """CV retrieval response"""
    id: int
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    job_title: Optional[str]
    skills: List[str]
    education: List[Dict]
    experience: List[Dict]
    created_at: datetime

    class Config:
        from_attributes = True

class CVListResponse(BaseModel):
    """List of CVs response"""
    total: int
    cvs: List[CVResponse]
