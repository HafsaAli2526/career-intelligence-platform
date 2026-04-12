from sqlalchemy import Column, Integer, String, Text, ARRAY, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base

class JDData(Base):
    """
    Job Description Model
    Stores parsed JD information from scraping/manual input
    """
    __tablename__ = "jd_data"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Job Information
    job_title = Column(String(200), index=True)
    company = Column(String(200), index=True)
    location = Column(String(200), index=True)
    
    # Salary Information (Pakistani formats)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default='PKR')
    salary_text = Column(String(200))  # Original text (e.g., "Competitive salary")
    
    # Required Skills
    required_skills = Column(ARRAY(String))  # Technical skills
    soft_skills = Column(ARRAY(String))  # Soft skills
    
    # Job Details
    responsibilities = Column(ARRAY(Text))
    experience_required = Column(String(50))  # e.g., "3-5 years"
    education_required = Column(String(200))
    
    # Work Type
    work_type = Column(String(50))  # remote/on-site/hybrid
    employment_type = Column(String(50))  # full-time/part-time/contract
    
    # Raw Data
    raw_text = Column(Text)  # Original JD text
    
    # Source Information
    source_url = Column(Text)
    source_platform = Column(String(50))  # rozee/indeed/mustakbil/manual
    
    # Vector Embedding
    embedding = Column(ARRAY(Float))
    
    # Timestamps
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<JDData(id={self.id}, title={self.job_title}, company={self.company})>"
