import re
import pdfplumber
import fitz  # PyMuPDF
from docx import Document
import spacy
from typing import Dict, List, Optional
from pathlib import Path
from app.utils.text_processing import clean_text, extract_emails, extract_phones
from app.utils.skill_dictionary import SkillDictionary
from app.services.embeddings import EmbeddingGenerator
import logging

logger = logging.getLogger(__name__)

class CVParser:
    """
    CV Parser Module
    Extracts: Job Title, Name, Contact, Skills, Education, Experience, etc.
    """
    
    def __init__(self):
        # Load SpaCy model
        try:
            self.nlp = spacy.load("en_core_web_lg")
            logger.info("✓ SpaCy model loaded")
        except:
            logger.warning("⚠ SpaCy model not found. Run: python -m spacy download en_core_web_lg")
            self.nlp = None
        
        # Load embeddings generator
        self.embedder = EmbeddingGenerator()
        
        # Load skills dictionary
        self.skills_dict = SkillDictionary()
    
    def parse_cv(self, file_path: str) -> Dict:
        """
        Main CV parsing function
        
        Args:
            file_path: Path to CV file (PDF/DOCX)
            
        Returns:
            Dictionary with all parsed CV fields
        """
        logger.info(f"Parsing CV: {file_path}")
        
        # Extract text
        text = self._extract_text(file_path)
        
        if not text:
            raise ValueError("Could not extract text from CV")
        
        # Parse all fields
        cv_data = {
            'raw_text': text,
            'full_name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'linkedin_url': self._extract_linkedin(text),
            'github_url': self._extract_github(text),
            'job_title': self._extract_job_title(text),
            'career_objective': self._extract_career_objective(text),
            'skills': self._extract_skills(text),
            'education': self._extract_education(text),
            'experience': self._extract_experience(text),
            'projects': self._extract_projects(text),
            'certifications': self._extract_certifications(text),
            'summary': self._generate_summary(text)
        }
        
        # Generate embedding
        cv_data['embedding'] = self.embedder.generate_cv_embedding(cv_data)
        
        logger.info(f"✓ CV parsed successfully: {cv_data.get('full_name')}")
        return cv_data
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX"""
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        
        if ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif ext == '.docx':
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyMuPDF: {e}")
            try:
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text()
            except Exception as e2:
                logger.error(f"PDF extraction failed: {e2}")
        
        return text
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX"""
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            return ""
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract full name using NER"""
        if not self.nlp:
            return None
        
        doc = self.nlp(text[:500])  # Check first 500 chars
        
        # Find PERSON entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        
        # Fallback: first line if it looks like a name
        first_line = text.split('\n')[0].strip()
        if len(first_line.split()) <= 4 and len(first_line) < 50:
            return first_line
        
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email"""
        emails = extract_emails(text)
        return emails[0] if emails else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        phones = extract_phones(text)
        return phones[0] if phones else None
    
    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn URL"""
        pattern = r'linkedin\.com/in/[\w-]+'
        matches = re.findall(pattern, text.lower())
        return f"https://{matches[0]}" if matches else None
    
    def _extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub URL"""
        pattern = r'github\.com/[\w-]+'
        matches = re.findall(pattern, text.lower())
        return f"https://{matches[0]}" if matches else None
    
    def _extract_job_title(self, text: str) -> Optional[str]:
        """
        Extract desired job title / career objective
        IMPORTANT: This is the expected role from CV
        """
        patterns = [
            r'(?:seeking|looking for|applying for|interested in)\s+(?:a|an|the)?\s*(?:position|role|job)\s+(?:of|as)?\s+([^\n.]{5,50})',
            r'(?:career objective|objective|goal)[\s:]+([^\n.]{10,100})',
            r'(?:desired position|target role)[\s:]+([^\n.]{5,50})',
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # Check first few lines for common job titles
        lines = text.split('\n')[:5]
        job_titles = [
            'software engineer', 'data scientist', 'web developer',
            'backend developer', 'frontend developer', 'full stack',
            'devops engineer', 'machine learning engineer', 'data analyst',
            'product manager', 'ui/ux designer', 'mobile developer'
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            for title in job_titles:
                if title in line_lower:
                    return line.strip()
        
        return None
    
    def _extract_career_objective(self, text: str) -> Optional[str]:
        """Extract career objective/summary"""
        patterns = [
            r'(?:objective|career objective|professional summary|summary)[\s:]+([^\n]+(?:\n[^\n]+){0,3})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return clean_text(matches[0])
        
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """
        Extract technical and soft skills
        Uses skills dictionary + NER
        """
        text_lower = text.lower()
        found_skills = set()
        
        # Match against skills dictionary
        all_skills = self.skills_dict.get_all_skills()
        for skill in all_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        # Extract from skills section specifically
        skills_section = self._extract_section(text, 'skills|technical skills|core competencies')
        if skills_section:
            tokens = re.split(r'[,;•\n\|]', skills_section)
            for token in tokens:
                token = token.strip().lower()
                if 2 < len(token) < 30:
                    found_skills.add(token)
        
        return sorted(list(found_skills))
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education details"""
        education_section = self._extract_section(text, 'education|academic')
        
        if not education_section:
            return []
        
        education = []
        
        # Degree patterns
        degree_patterns = [
            r'(bachelor|master|phd|b\.?sc|m\.?sc|b\.?tech|m\.?tech|bba|mba).*?(?:in|of)?\s+([^\n.]{5,50})',
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, education_section, re.IGNORECASE)
            for match in matches:
                education.append({
                    'degree': f"{match[0]} in {match[1]}",
                    'institution': self._find_nearby_org(education_section),
                    'years': self._extract_years(education_section)
                })
        
        return education
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        exp_section = self._extract_section(text, 'experience|work experience|employment')
        
        if not exp_section:
            return []
        
        if not self.nlp:
            return []
        
        doc = self.nlp(exp_section)
        
        experiences = []
        orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
        
        lines = exp_section.split('\n')
        current_exp = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_exp:
                    experiences.append(current_exp)
                    current_exp = {}
                continue
            
            # Check for job title
            if any(title in line.lower() for title in ['engineer', 'developer', 'manager', 'analyst', 'designer']):
                current_exp['role'] = line
            
            # Check for company
            if any(org.lower() in line.lower() for org in orgs):
                current_exp['company'] = line
            
            # Check for duration
            years = self._extract_years(line)
            if years:
                current_exp['duration'] = years
        
        if current_exp:
            experiences.append(current_exp)
        
        return experiences
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract projects"""
        proj_section = self._extract_section(text, 'projects|personal projects')
        
        if not proj_section:
            return []
        
        projects = []
        lines = proj_section.split('\n')
        
        current_project = {}
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                if not current_project:
                    current_project['title'] = line
                else:
                    current_project['description'] = line
                    projects.append(current_project)
                    current_project = {}
        
        return projects
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        cert_section = self._extract_section(text, 'certifications|certificates')
        
        if not cert_section:
            return []
        
        certs = re.split(r'[\n•\-]', cert_section)
        return [cert.strip() for cert in certs if cert.strip() and len(cert.strip()) > 5]
    
    def _extract_section(self, text: str, section_name: str) -> Optional[str]:
        """Extract specific section from CV"""
        pattern = rf'(?:{section_name})[\s:]*\n(.*?)(?:\n[A-Z][a-z]+[\s:]|\Z)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else None
    
    def _extract_years(self, text: str) -> Optional[str]:
        """Extract year ranges"""
        patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4})',
            r'(\d{4})\s*[-–]\s*(present|current)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _find_nearby_org(self, text: str) -> Optional[str]:
        """Find organization name using NER"""
        if not self.nlp:
            return None
        
        doc = self.nlp(text[:500])
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                return ent.text
        
        return None
    
    def _generate_summary(self, text: str) -> str:
        """Generate brief summary (first 500 chars)"""
        return text[:500].strip()
