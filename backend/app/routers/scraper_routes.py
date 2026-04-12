from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.jd import JDData
from app.services.jd_parser import JDParser
from scrapers.job_scrapers import UnifiedJobScraper

router = APIRouter(prefix="/api/scrape", tags=["Job Scraping"])

# Initialize services
job_scraper = UnifiedJobScraper()
jd_parser = JDParser()


@router.post("/jobs")
async def scrape_jobs(
    background_tasks: BackgroundTasks,
    keyword: str = "python",
    location: str = "karachi",
    pages: int = 2,
    db: Session = Depends(get_db)
):
    """
    Scrape jobs from Pakistani job boards
    Runs in background
    """
    
    def scrape_and_save():
        """Background task to scrape and save jobs"""
        try:
            # Scrape jobs
            jobs = job_scraper.scrape_all(keyword, location, pages)
            
            # Parse and save each job
            for job in jobs:
                # Parse the job description
                jd_data = jd_parser.parse_jd(
                    job.get('raw_text', ''),
                    source_url=job.get('source_url'),
                    source_platform=job.get('source_platform')
                )
                
                # Save to database
                salary_info = jd_data.get('salary_info', {})
                
                jd_record = JDData(
                    job_title=job.get('job_title') or jd_data.get('job_title'),
                    company=job.get('company') or jd_data.get('company'),
                    location=job.get('location') or jd_data.get('location'),
                    salary_min=salary_info.get('min'),
                    salary_max=salary_info.get('max'),
                    salary_text=salary_info.get('text') or job.get('salary_text'),
                    required_skills=jd_data.get('required_skills', []),
                    soft_skills=jd_data.get('soft_skills', []),
                    responsibilities=jd_data.get('responsibilities', []),
                    experience_required=jd_data.get('experience_required'),
                    education_required=jd_data.get('education_required'),
                    work_type=jd_data.get('work_type'),
                    employment_type=jd_data.get('employment_type'),
                    raw_text=job.get('raw_text', ''),
                    source_url=job.get('source_url'),
                    source_platform=job.get('source_platform'),
                    embedding=jd_data.get('embedding')
                )
                
                db.add(jd_record)
            
            db.commit()
            
        except Exception as e:
            print(f"Error in scraping task: {e}")
    
    # Add to background tasks
    background_tasks.add_task(scrape_and_save)
    
    return {
        "message": "Job scraping started in background",
        "status": "processing",
        "parameters": {
            "keyword": keyword,
            "location": location,
            "pages": pages
        }
    }


@router.get("/status")
async def scraping_status(db: Session = Depends(get_db)):
    """Get scraping statistics"""
    total_jobs = db.query(JDData).count()
    recent_jobs = db.query(JDData)\
        .order_by(JDData.scraped_at.desc())\
        .limit(10)\
        .all()
    
    return {
        "total_jobs": total_jobs,
        "recent_jobs": [
            {
                "id": job.id,
                "title": job.job_title,
                "company": job.company,
                "source": job.source_platform,
                "scraped_at": job.scraped_at
            }
            for job in recent_jobs
        ]
    }