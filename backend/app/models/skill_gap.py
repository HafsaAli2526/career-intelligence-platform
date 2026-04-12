from sqlalchemy import Column, Integer, String, Text, ARRAY, ForeignKey, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base

class SkillGap(Base):
    """
    Skill Gap Model
    Stores identified skill gaps for CV-JD pairs
    """
    __tablename__ = "skill_gap"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    cv_id = Column(Integer, ForeignKey('cv_data.id'), nullable=False)
    jd_id = Column(Integer, ForeignKey('jd_data.id'), nullable=False)
    
    # Missing Skills (Categorized)
    missing_technical_skills = Column(ARRAY(String))
    missing_tools = Column(ARRAY(String))
    missing_soft_skills = Column(ARRAY(String))
    missing_domain_knowledge = Column(ARRAY(String))
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SkillGap(cv_id={self.cv_id}, jd_id={self.jd_id})>"


class CourseData(Base):
    """
    Course Data Model
    Stores course information for RAG recommendations
    """
    __tablename__ = "course_data"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Course Information
    course_title = Column(String(300))
    provider = Column(String(100))  # Coursera, DigiSkills, YouTube, etc.
    description = Column(Text)
    url = Column(Text)
    
    # Skills Covered
    skills_covered = Column(ARRAY(String))
    
    # Course Details
    duration_hours = Column(Integer)
    level = Column(String(50))  # beginner/intermediate/advanced
    language = Column(String(50), default='English')
    
    # Pricing
    is_free = Column(Integer, default=1)  # 1=free, 0=paid
    price = Column(Float, nullable=True)
    
    # Vector Embedding
    embedding = Column(ARRAY(Float))
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<CourseData(id={self.id}, title={self.course_title})>"


class SalaryStats(Base):
    """
    Salary Statistics Model
    Aggregated salary data for analytics
    """
    __tablename__ = "salary_stats"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Job Information
    job_title = Column(String(200), index=True)
    location = Column(String(200))
    
    # Salary Range
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    avg_salary = Column(Integer)
    median_salary = Column(Integer, nullable=True)
    
    # Metadata
    currency = Column(String(10), default='PKR')
    sample_count = Column(Integer)  # Number of JDs used for calculation
    
    # Timestamp
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SalaryStats(title={self.job_title}, avg={self.avg_salary})>"

