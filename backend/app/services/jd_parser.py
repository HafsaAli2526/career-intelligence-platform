import re
import spacy
from typing import Dict, List, Optional
from app.utils.text_processing import clean_text
from app.utils.salary_extractor import SalaryExtractor
from app.utils.skill_dictionary import SkillDictionary
from app.services.embeddings import EmbeddingGenerator
import logging

logger = logging.getLogger(__name__)

class JDParser:
    """
    JD Parser Module
    Extracts: Job Title, Company, Location, Skills, Salary, Experience, etc.
    """
    
    def __init__(self):
        # Load SpaCy
        try:
            self.nlp = spacy.load("en_core_web_lg")
            logger.info("✓ SpaCy model loaded for JD parsing")
        except:
            logger.warning("⚠ SpaCy model not found")
            self.nlp = None
        
        # Initialize utilities
        self.salary_extractor = SalaryExtractor()
        self.skills_dict = SkillDictionary()
        self.embedder = EmbeddingGenerator()
        
        # Load skill categories
        self.technical_skills = self._load_technical_skills()
        self.soft_skills = self._load_soft_skills()
    
    def _load_technical_skills(self) -> set:
        """Get technical skills from dictionary"""
        tech_categories = ['programming_languages', 'web_frontend', 'web_backend', 
                          'mobile', 'databases', 'cloud_devops', 'data_ml']
        skills = set()
        for cat in tech_categories:
            skills.update(self.skills_dict.get_skills_by_category(cat))
        return skills
    
    def _load_soft_skills(self) -> set:
        """Get soft skills from dictionary"""
        return set(self.skills_dict.get_skills_by_category('soft_skills'))
    
    def parse_jd(self, jd_text: str, source_url: str = None, 
                 source_platform: str = None) -> Dict:
        """
        Main JD parsing function
        
        Args:
            jd_text: Raw job description text
            source_url: Optional source URL
            source_platform: rozee/indeed/mustakbil/manual
            
        Returns:
            Dictionary with all parsed JD fields
        """
        logger.info(f"Parsing JD from {source_platform}")
        
        jd_data = {
            'raw_text': jd_text,
            'job_title': self._extract_job_title(jd_text),
            'company': self._extract_company(jd_text),
            'location': self._extract_location(jd_text),
            'salary_info': self.salary_extractor.extract(jd_text),
            'required_skills': self._extract_technical_skills(jd_text),
            'soft_skills': self._extract_soft_skills(jd_text),
            'responsibilities': self._extract_responsibilities(jd_text),
            'experience_required': self._extract_experience(jd_text),
            'education_required': self._extract_education(jd_text),
            'work_type': self._extract_work_type(jd_text),
            'employment_type': self._extract_employment_type(jd_text),
            'source_url': source_url,
            'source_platform': source_platform
        }
        
        # Generate embedding
        jd_data['embedding'] = self.embedder.generate_jd_embedding(jd_data)
        
        logger.info(f"✓ JD parsed: {jd_data.get('job_title')}")
        return jd_data
    
    def _extract_job_title(self, text: str) -> Optional[str]:
        """Extract job title"""
        patterns = [
            r'^([A-Z][^\n]{10,80}?)(?:\n|$)',
            r'(?:position|job title|role)[\s:]+([^\n]{5,80})',
            r'(?:we are looking for|hiring|seeking)\s+(?:a|an)?\s*([^\n]{10,60})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                title = match.group(1).strip()
                title = re.sub(r'^(job title|position|role)[\s:]*', '', title, flags=re.IGNORECASE)
                return clean_text(title)
        
        return None
    
    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name using NER"""
        if not self.nlp:
            return None
        
        doc = self.nlp(text[:500])
        orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
        return orgs[0] if orgs else None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract job location"""
        # Pakistani cities
        pakistan_cities = [
            'karachi', 'lahore', 'islamabad', 'rawalpindi', 'faisalabad',
            'multan', 'peshawar', 'quetta', 'sialkot', 'gujranwala',
            'hyderabad', 'sargodha', 'bahawalpur'
        ]
        
        text_lower = text.lower()
        for city in pakistan_cities:
            if city in text_lower:
                return city.title()
        
        # Use NER as fallback
        if self.nlp:
            doc = self.nlp(text)
            locations = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
            return locations[0] if locations else None
        
        return None
    
    def _extract_technical_skills(self, text: str) -> List[str]:
        """Extract technical skills"""
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.technical_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        return sorted(list(found_skills))
    
    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extract soft skills"""
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.soft_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        return sorted(list(found_skills))
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract responsibilities"""
        resp_section = self._extract_section(text, 'responsibilities|duties|role')
        
        if not resp_section:
            return []
        
        lines = re.split(r'[\n•\-]', resp_section)
        responsibilities = [line.strip() for line in lines if len(line.strip()) > 20]
        
        return responsibilities[:10]
    
    def _extract_experience(self, text: str) -> Optional[str]:
        """Extract required experience"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience[\s:]+(\d+)\+?\s*(?:years?|yrs?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{match.group(1)}+ years"
        
        if re.search(r'fresh graduate|entry level', text, re.IGNORECASE):
            return "0-1 years"
        
        return None
    
    def _extract_education(self, text: str) -> Optional[str]:
        """Extract education requirements"""
        pattern = r'(bachelor|master|phd|b\.?sc|m\.?sc).*?(?:in|of)?\s+([^\n.]{5,50})'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0).strip() if match else None
    
    def _extract_work_type(self, text: str) -> Optional[str]:
        """Extract work type"""
        text_lower = text.lower()
        if 'remote' in text_lower:
            return 'remote'
        elif 'hybrid' in text_lower:
            return 'hybrid'
        elif 'on-site' in text_lower or 'onsite' in text_lower:
            return 'on-site'
        return None
    
    def _extract_employment_type(self, text: str) -> Optional[str]:
        """Extract employment type"""
        text_lower = text.lower()
        if 'full-time' in text_lower or 'full time' in text_lower:
            return 'full-time'
        elif 'part-time' in text_lower:
            return 'part-time'
        elif 'contract' in text_lower:
            return 'contract'
        return 'full-time'
    
    def _extract_section(self, text: str, section_keywords: str) -> Optional[str]:
        """Extract specific section"""
        pattern = rf'(?:{section_keywords})[\s:]*\n(.*?)(?:\n[A-Z][a-z]+[\s:]|\Z)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else None
