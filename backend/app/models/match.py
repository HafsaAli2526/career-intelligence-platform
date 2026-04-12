from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Match(Base):
    """
    CV-JD Match Model
    Stores matching results between CVs and JDs
    
    Formula: 0.6 × semantic + 0.3 × skills + 0.1 × title
    """
    __tablename__ = "matches"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    cv_id = Column(Integer, ForeignKey('cv_data.id'), nullable=False, index=True)
    jd_id = Column(Integer, ForeignKey('jd_data.id'), nullable=False, index=True)
    
    # Component Scores (0-1 range)
    semantic_score = Column(Float)  # Embedding similarity
    skill_overlap_score = Column(Float)  # Skill matching
    title_match_score = Column(Float)  # Title similarity
    
    # Final Score (0-1 range)
    final_score = Column(Float, index=True)
    
    # Ranking
    rank = Column(Integer)  # Rank for this CV
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Match(cv_id={self.cv_id}, jd_id={self.jd_id}, score={self.final_score})>"
