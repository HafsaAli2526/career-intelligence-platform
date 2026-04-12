from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, ARRAY, String, Boolean
from sqlalchemy.sql import func
from app.database import Base

class ATSScore(Base):
    """
    ATS Score Model
    Stores ATS evaluation results (0-100 score)
    
    Formula: 40% skill + 25% title + 15% exp + 10% edu + 10% tools
    """
    __tablename__ = "ats_scores"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    cv_id = Column(Integer, ForeignKey('cv_data.id'), nullable=False, index=True)
    jd_id = Column(Integer, ForeignKey('jd_data.id'), nullable=False, index=True)
    
    # Overall ATS Score (0-100)
    ats_score = Column(Float, nullable=False, index=True)
    
    # Component Scores (0-100 each)
    skill_match_score = Column(Float)  # 40% weight
    title_alignment = Column(Float)    # 25% weight
    experience_score = Column(Float)   # 15% weight
    education_score = Column(Float)    # 10% weight
    tools_match_score = Column(Float)  # 10% weight
    
    # Detailed Skill Analysis
    common_skills = Column(ARRAY(String))  # Skills present in both
    missing_skills = Column(ARRAY(String))  # Skills in JD but not in CV
    matched_tools = Column(ARRAY(String))  # Matched tools/technologies
    
    # Boolean Checks
    title_match = Column(Boolean, default=False)
    experience_match = Column(Boolean, default=False)
    education_match = Column(Boolean, default=False)
    
    # Experience Details
    years_required = Column(Integer)
    years_achieved = Column(Integer)
    
    # Title Similarity (0-1)
    title_similarity = Column(Float)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ATSScore(cv_id={self.cv_id}, jd_id={self.jd_id}, score={self.ats_score})>"