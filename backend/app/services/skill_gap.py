
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)

class SkillGapAnalyzer:
    """
    Skill Gap Analyzer
    Identifies missing skills: jd.skills - cv.skills
    Categorizes into: Technical, Tools, Soft Skills, Domain
    """
    
    def __init__(self):
        self.skill_categories = {
            'programming': ['python', 'java', 'javascript', 'typescript', 'c++'],
            'web': ['react', 'angular', 'vue', 'nodejs', 'django', 'flask'],
            'database': ['postgresql', 'mysql', 'mongodb', 'redis'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'ml': ['machine learning', 'tensorflow', 'pytorch'],
            'tools': ['git', 'jira', 'jenkins', 'ci/cd']
        }
    
    def analyze_gap(self, cv_data: Dict, jd_data: Dict) -> Dict:
        """
        Analyze skill gaps between CV and JD
        
        Returns categorized gaps with priority and severity
        """
        logger.info("Analyzing skill gaps")
        
        cv_skills = set(s.lower() for s in cv_data.get('skills', []))
        jd_required = set(s.lower() for s in jd_data.get('required_skills', []))
        jd_soft = set(s.lower() for s in jd_data.get('soft_skills', []))
        
        # Compute missing skills
        missing_technical = jd_required - cv_skills
        missing_soft = jd_soft - cv_skills
        
        # Categorize
        categorized_gaps = self._categorize_skills(missing_technical)
        
        # Priority
        priority_skills = self._determine_priority(missing_technical, jd_data)
        
        # Severity
        gap_severity = self._calculate_severity(len(missing_technical), len(jd_required))
        
        logger.info(f"✓ Found {len(missing_technical)} technical gaps, severity: {gap_severity}")
        
        return {
            'missing_technical_skills': sorted(list(missing_technical)),
            'missing_soft_skills': sorted(list(missing_soft)),
            'categorized_gaps': categorized_gaps,
            'priority_skills': priority_skills,
            'gap_severity': gap_severity,
            'total_missing': len(missing_technical) + len(missing_soft),
            'match_percentage': self._calculate_match_percentage(cv_skills, jd_required)
        }
    
    def _categorize_skills(self, missing_skills: Set[str]) -> Dict:
        """Categorize missing skills"""
        categorized = {
            'programming_languages': [],
            'web_technologies': [],
            'databases': [],
            'cloud_devops': [],
            'ml_ai': [],
            'tools': [],
            'other': []
        }
        
        for skill in missing_skills:
            categorized_flag = False
            
            if any(s in skill for s in self.skill_categories['programming']):
                categorized['programming_languages'].append(skill)
                categorized_flag = True
            
            if any(s in skill for s in self.skill_categories['web']):
                categorized['web_technologies'].append(skill)
                categorized_flag = True
            
            if any(s in skill for s in self.skill_categories['database']):
                categorized['databases'].append(skill)
                categorized_flag = True
            
            if any(s in skill for s in self.skill_categories['cloud']):
                categorized['cloud_devops'].append(skill)
                categorized_flag = True
            
            if any(s in skill for s in self.skill_categories['ml']):
                categorized['ml_ai'].append(skill)
                categorized_flag = True
            
            if any(s in skill for s in self.skill_categories['tools']):
                categorized['tools'].append(skill)
                categorized_flag = True
            
            if not categorized_flag:
                categorized['other'].append(skill)
        
        return {k: v for k, v in categorized.items() if v}
    
    def _determine_priority(self, missing_skills: Set[str], jd_data: Dict) -> List[str]:
        """Determine priority skills (top 5)"""
        job_title = jd_data.get('job_title', '').lower()
        
        priority = []
        for skill in missing_skills:
            if skill in job_title:
                priority.append(skill)
        
        for skill in missing_skills:
            if skill not in priority:
                priority.append(skill)
        
        return priority[:5]
    
    def _calculate_severity(self, missing_count: int, total_required: int) -> str:
        """Calculate gap severity"""
        if total_required == 0:
            return 'low'
        
        gap_ratio = missing_count / total_required
        
        if gap_ratio < 0.2:
            return 'low'
        elif gap_ratio < 0.5:
            return 'medium'
        else:
            return 'high'
    
    def _calculate_match_percentage(self, cv_skills: Set[str], 
                                   required_skills: Set[str]) -> float:
        """Calculate match percentage"""
        if not required_skills:
            return 100.0
        
        matching = cv_skills.intersection(required_skills)
        return round((len(matching) / len(required_skills)) * 100, 2)