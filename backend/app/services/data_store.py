from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.cv import CVData
from app.models.jd import JDData
from app.models.match import Match
from app.models.skill_gap import SkillGap
from app.models.ats_score import ATSScore
import logging

logger = logging.getLogger(__name__)

class CVDataStore:
    """CV Data Store - Manages CV persistence"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def store_cv(self, parsed_cv_data: Dict) -> int:
        """Store parsed CV to database"""
        try:
            cv_record = CVData(
                full_name=parsed_cv_data.get('full_name'),
                email=parsed_cv_data.get('email'),
                phone=parsed_cv_data.get('phone'),
                linkedin_url=parsed_cv_data.get('linkedin_url'),
                github_url=parsed_cv_data.get('github_url'),
                job_title=parsed_cv_data.get('job_title'),
                career_objective=parsed_cv_data.get('career_objective'),
                skills=parsed_cv_data.get('skills', []),
                education=parsed_cv_data.get('education', []),
                experience=parsed_cv_data.get('experience', []),
                projects=parsed_cv_data.get('projects', []),
                certifications=parsed_cv_data.get('certifications', []),
                summary=parsed_cv_data.get('summary'),
                raw_text=parsed_cv_data.get('raw_text'),
                embedding=parsed_cv_data.get('embedding')
            )
            
            self.db.add(cv_record)
            self.db.commit()
            self.db.refresh(cv_record)
            
            logger.info(f"✓ CV stored: ID={cv_record.id}")
            return cv_record.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"CV storage failed: {e}")
            raise
    
    def get_cv(self, cv_id: int) -> Optional[Dict]:
        """Retrieve CV by ID"""
        cv = self.db.query(CVData).filter(CVData.id == cv_id).first()
        if not cv:
            return None
        
        return {
            'id': cv.id,
            'full_name': cv.full_name,
            'email': cv.email,
            'phone': cv.phone,
            'job_title': cv.job_title,
            'skills': cv.skills,
            'education': cv.education,
            'experience': cv.experience,
            'embedding': cv.embedding
        }
    
    def get_all_cvs(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Retrieve all CVs"""
        cvs = self.db.query(CVData).offset(skip).limit(limit).all()
        return [self.get_cv(cv.id) for cv in cvs]


class JDDataStore:
    """JD Data Store - Manages JD persistence"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def store_jd(self, parsed_jd_data: Dict) -> int:
        """Store parsed JD to database"""
        try:
            salary_info = parsed_jd_data.get('salary_info', {})
            
            jd_record = JDData(
                job_title=parsed_jd_data.get('job_title'),
                company=parsed_jd_data.get('company'),
                location=parsed_jd_data.get('location'),
                salary_min=salary_info.get('min'),
                salary_max=salary_info.get('max'),
                salary_currency=salary_info.get('currency', 'PKR'),
                salary_text=salary_info.get('text'),
                required_skills=parsed_jd_data.get('required_skills', []),
                soft_skills=parsed_jd_data.get('soft_skills', []),
                responsibilities=parsed_jd_data.get('responsibilities', []),
                experience_required=parsed_jd_data.get('experience_required'),
                education_required=parsed_jd_data.get('education_required'),
                work_type=parsed_jd_data.get('work_type'),
                employment_type=parsed_jd_data.get('employment_type'),
                raw_text=parsed_jd_data.get('raw_text'),
                source_url=parsed_jd_data.get('source_url'),
                source_platform=parsed_jd_data.get('source_platform'),
                embedding=parsed_jd_data.get('embedding')
            )
            
            self.db.add(jd_record)
            self.db.commit()
            self.db.refresh(jd_record)
            
            logger.info(f"✓ JD stored: ID={jd_record.id}")
            return jd_record.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"JD storage failed: {e}")
            raise
    
    def get_jd(self, jd_id: int) -> Optional[Dict]:
        """Retrieve JD by ID"""
        jd = self.db.query(JDData).filter(JDData.id == jd_id).first()
        if not jd:
            return None
        
        return {
            'id': jd.id,
            'job_title': jd.job_title,
            'company': jd.company,
            'location': jd.location,
            'salary_min': jd.salary_min,
            'salary_max': jd.salary_max,
            'salary_text': jd.salary_text,
            'required_skills': jd.required_skills,
            'soft_skills': jd.soft_skills,
            'experience_required': jd.experience_required,
            'embedding': jd.embedding
        }
    
    def get_all_jds(self, skip: int = 0, limit: int = 1000) -> List[Dict]:
        """Retrieve all JDs"""
        jds = self.db.query(JDData).offset(skip).limit(limit).all()
        return [self.get_jd(jd.id) for jd in jds]


class ResultsDataStore:
    """Results Data Store - Manages ATS, Match, Skill Gap results"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def store_ats_score(self, cv_id: int, jd_id: int, ats_result: Dict) -> int:
        """Store ATS score"""
        try:
            ats_record = ATSScore(
                cv_id=cv_id,
                jd_id=jd_id,
                ats_score=ats_result['ats_score'],
                skill_match_score=ats_result['skill_match_score'],
                title_alignment=ats_result['title_alignment'],
                experience_score=ats_result.get('experience_score', 0),
                education_score=ats_result.get('education_score', 0),
                tools_match_score=ats_result['tools_match_score'],
                common_skills=ats_result['common_skills'],
                missing_skills=ats_result['missing_skills'],
                matched_tools=ats_result['matched_tools'],
                title_match=ats_result.get('title_match', False),
                experience_match=ats_result['experience_match'],
                education_match=ats_result['education_match'],
                years_required=ats_result.get('years_required', 0),
                years_achieved=ats_result.get('years_achieved', 0),
                title_similarity=ats_result['title_similarity']
            )
            
            self.db.add(ats_record)
            self.db.commit()
            self.db.refresh(ats_record)
            
            logger.info(f"✓ ATS score stored: {ats_result['ats_score']}/100")
            return ats_record.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"ATS score storage failed: {e}")
            raise
    
    def store_match(self, cv_id: int, jd_id: int, match_result: Dict) -> int:
        """Store match result"""
        try:
            match_record = Match(
                cv_id=cv_id,
                jd_id=jd_id,
                semantic_score=match_result['semantic_score'],
                skill_overlap_score=match_result['skill_overlap_score'],
                title_match_score=match_result['title_match_score'],
                final_score=match_result['final_score'],
                rank=match_result.get('rank', 0)
            )
            
            self.db.add(match_record)
            self.db.commit()
            self.db.refresh(match_record)
            
            return match_record.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"Match storage failed: {e}")
            raise
    
    def store_skill_gap(self, cv_id: int, jd_id: int, gap_result: Dict) -> int:
        """Store skill gap"""
        try:
            gap_record = SkillGap(
                cv_id=cv_id,
                jd_id=jd_id,
                missing_technical_skills=gap_result['missing_technical_skills'],
                missing_soft_skills=gap_result['missing_soft_skills'],
                missing_tools=gap_result.get('categorized_gaps', {}).get('tools', []),
                missing_domain_knowledge=gap_result.get('categorized_gaps', {}).get('other', [])
            )
            
            self.db.add(gap_record)
            self.db.commit()
            self.db.refresh(gap_record)
            
            logger.info(f"✓ Skill gap stored: {len(gap_result['missing_technical_skills'])} gaps")
            return gap_record.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"Skill gap storage failed: {e}")
            raise