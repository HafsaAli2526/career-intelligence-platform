from sqlalchemy import Column, Integer, String, Text, ARRAY, JSON, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base

class CVData(Base):
    """
    CV Data Model
    Stores parsed CV information with embeddings
    """
    __tablename__ = "cv_data"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # User Information
    user_id = Column(String(100), nullable=True, index=True)
    full_name = Column(String(200))
    email = Column(String(150), index=True)
    phone = Column(String(50))
    
    # Social Links
    linkedin_url = Column(Text)
    github_url = Column(Text)
    
    # Career Information
    job_title = Column(String(200), index=True)  # Expected role / Career objective
    career_objective = Column(Text)
    summary = Column(Text)
    
    # Skills & Competencies
    skills = Column(ARRAY(String))  # All skills (technical + soft)
    
    # Education (JSON array)
    # Format: [{"degree": "...", "institution": "...", "years": "..."}]
    education = Column(JSON)
    
    # Work Experience (JSON array)
    # Format: [{"role": "...", "company": "...", "duration": "..."}]
    experience = Column(JSON)
    
    # Projects (JSON array)
    projects = Column(JSON)
    
    # Certifications
    certifications = Column(ARRAY(String))
    
    # Raw Data
    raw_text = Column(Text)  # Original CV text
    
    # Vector Embedding
    embedding = Column(ARRAY(Float))  # Sentence-BERT embedding
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<CVData(id={self.id}, name={self.full_name}, title={self.job_title})>"
