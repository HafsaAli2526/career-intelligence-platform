
from typing import Dict, List
from difflib import SequenceMatcher
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class ATSScorer:
    """
    ATS Scoring System (0-100)
    Evaluates CV against ONE JD
    """
    
    def __init__(self):
        self.weights = {
            'skill_match': settings.ATS_WEIGHT_SKILLS,      # 0.40
            'title_alignment': settings.ATS_WEIGHT_TITLE,   # 0.25
            'experience_alignment': settings.ATS_WEIGHT_EXPERIENCE,  # 0.15
            'education_alignment': settings.ATS_WEIGHT_EDUCATION,    # 0.10
            'tools_match': settings.ATS_WEIGHT_TOOLS        # 0.10
        }
        logger.info(f"ATS Scorer initialized with weights: {self.weights}")
    
    def compute_ats_score(self, cv_data: Dict, jd_data: Dict) -> Dict:
        """
        Compute ATS score (0-100)
        
        Returns full breakdown with all component scores
        """
        logger.info("Computing ATS score")
        
        # 1. Skill Match (40%)
        skill_result = self._compute_skill_match(
            cv_data.get('skills', []),
            jd_data.get('required_skills', [])
        )
        
        # 2. Title Alignment (25%)
        title_score = self._compute_title_alignment(
            cv_data.get('job_title'),
            jd_data.get('job_title'),
            cv_data.get('embedding'),
            jd_data.get('embedding')
        )
        
        # 3. Experience Alignment (15%)
        exp_result = self._compute_experience_alignment(
            cv_data.get('experience', []),
            jd_data.get('experience_required')
        )
        
        # 4. Education Alignment (10%)
        edu_result = self._compute_education_alignment(
            cv_data.get('education', []),
            jd_data.get('education_required')
        )
        
        # 5. Tools Match (10%)
        tools_result = self._compute_tools_match(
            cv_data.get('skills', []),
            jd_data.get('required_skills', [])
        )
        
        # Calculate final ATS score
        ats_score = (
            self.weights['skill_match'] * skill_result['score'] +
            self.weights['title_alignment'] * title_score +
            self.weights['experience_alignment'] * exp_result['score'] +
            self.weights['education_alignment'] * edu_result['score'] +
            self.weights['tools_match'] * tools_result['score']
        )
        
        logger.info(f"✓ ATS Score computed: {ats_score:.2f}/100")
        
        return {
            'ats_score': round(ats_score, 2),
            'skill_match_score': round(skill_result['score'], 2),
            'common_skills': skill_result['common_skills'],
            'missing_skills': skill_result['missing_skills'],
            'title_alignment': round(title_score, 2),
            'title_similarity': round(title_score / 100, 2),
            'experience_match': exp_result['match'],
            'experience_score': round(exp_result['score'], 2),
            'years_required': exp_result['years_required'],
            'years_achieved': exp_result['years_achieved'],
            'education_match': edu_result['match'],
            'education_score': round(edu_result['score'], 2),
            'tools_match_score': round(tools_result['score'], 2),
            'matched_tools': tools_result['matched_tools'],
            'breakdown': {
                'skill_match': f"{round(skill_result['score'], 1)}% (weight: 40%)",
                'title_alignment': f"{round(title_score, 1)}% (weight: 25%)",
                'experience_alignment': f"{round(exp_result['score'], 1)}% (weight: 15%)",
                'education_alignment': f"{round(edu_result['score'], 1)}% (weight: 10%)",
                'tools_match': f"{round(tools_result['score'], 1)}% (weight: 10%)"
            }
        }
    
    def _compute_skill_match(self, cv_skills: List[str], jd_skills: List[str]) -> Dict:
        """Skill match: (common_skills / total_required_skills) * 100"""
        if not jd_skills:
            return {'score': 0.0, 'common_skills': [], 'missing_skills': []}
        
        cv_skills_set = set(s.lower().strip() for s in cv_skills)
        jd_skills_set = set(s.lower().strip() for s in jd_skills)
        
        common_skills = cv_skills_set.intersection(jd_skills_set)
        missing_skills = jd_skills_set - cv_skills_set
        
        score = (len(common_skills) / len(jd_skills_set)) * 100
        
        return {
            'score': score,
            'common_skills': sorted(list(common_skills)),
            'missing_skills': sorted(list(missing_skills))
        }
    
    def _compute_title_alignment(self, cv_title: str, jd_title: str,
                                 cv_embedding: List[float] = None,
                                 jd_embedding: List[float] = None) -> float:
        """Title alignment using semantic + string similarity"""
        if not cv_title or not jd_title:
            return 0.0
        
        cv_title = cv_title.lower().strip()
        jd_title = jd_title.lower().strip()
        
        # String similarity
        string_sim = SequenceMatcher(None, cv_title, jd_title).ratio()
        
        # Semantic similarity
        semantic_score = 0.0
        if cv_embedding and jd_embedding:
            try:
                cv_vec = np.array(cv_embedding).reshape(1, -1)
                jd_vec = np.array(jd_embedding).reshape(1, -1)
                semantic_score = cosine_similarity(cv_vec, jd_vec)[0][0]
                semantic_score = max(0, min(1, semantic_score))
            except:
                semantic_score = 0.0
        
        # Keyword matching
        keywords = ['developer', 'engineer', 'analyst', 'manager']
        cv_kw = set(kw for kw in keywords if kw in cv_title)
        jd_kw = set(kw for kw in keywords if kw in jd_title)
        keyword_match = len(cv_kw.intersection(jd_kw)) / max(len(jd_kw), 1)
        
        # Combined score
        final_score = (
            0.50 * semantic_score * 100 +
            0.30 * string_sim * 100 +
            0.20 * keyword_match * 100
        )
        
        return min(100.0, final_score)
    
    def _compute_experience_alignment(self, cv_experience: List[Dict],
                                     jd_experience_required: str) -> Dict:
        """Compare years required vs achieved"""
        import re
        
        # Extract years from CV
        total_years = 0
        if cv_experience:
            for exp in cv_experience:
                duration = exp.get('duration', '')
                if duration:
                    years_match = re.search(r'(\d+)\s*(?:years?|yrs?)', duration, re.IGNORECASE)
                    if years_match:
                        total_years += int(years_match.group(1))
        
        # Extract required years from JD
        required_years = 0
        if jd_experience_required:
            years_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)', 
                                   jd_experience_required, re.IGNORECASE)
            if years_match:
                required_years = int(years_match.group(1))
        
        # Calculate score
        if required_years == 0:
            score, match = 100.0, True
        elif total_years >= required_years:
            score, match = 100.0, True
        elif total_years >= required_years * 0.8:
            score, match = 80.0, True
        else:
            score = (total_years / required_years) * 100 if required_years > 0 else 0
            match = False
        
        return {
            'score': min(100.0, score),
            'match': match,
            'years_required': required_years,
            'years_achieved': total_years
        }
    
    def _compute_education_alignment(self, cv_education: List[Dict],
                                    jd_education_required: str) -> Dict:
        """Check education level match"""
        if not jd_education_required:
            return {'score': 100.0, 'match': True}
        
        if not cv_education:
            return {'score': 0.0, 'match': False}
        
        # Education hierarchy
        edu_levels = {
            'phd': 5, 'doctorate': 5,
            'master': 4, 'msc': 4, 'mtech': 4, 'mba': 4,
            'bachelor': 3, 'bsc': 3, 'btech': 3, 'bba': 3,
            'associate': 2, 'diploma': 1
        }
        
        # Get highest CV education
        cv_level = 0
        for edu in cv_education:
            degree = edu.get('degree', '').lower()
            for key, level in edu_levels.items():
                if key in degree:
                    cv_level = max(cv_level, level)
        
        # Get required level
        jd_edu_lower = jd_education_required.lower()
        required_level = 0
        for key, level in edu_levels.items():
            if key in jd_edu_lower:
                required_level = max(required_level, level)
        
        # Calculate match
        if required_level == 0:
            score, match = 100.0, True
        elif cv_level >= required_level:
            score, match = 100.0, True
        else:
            score = (cv_level / required_level) * 100 if required_level > 0 else 0
            match = False
        
        return {'score': min(100.0, score), 'match': match}
    
    def _compute_tools_match(self, cv_skills: List[str], jd_skills: List[str]) -> Dict:
        """Match tools and technologies"""
        tools_keywords = [
            'git', 'docker', 'kubernetes', 'jenkins', 'jira', 'aws', 'azure',
            'gcp', 'mongodb', 'postgresql', 'mysql', 'redis', 'linux'
        ]
        
        cv_skills_lower = [s.lower().strip() for s in cv_skills]
        jd_skills_lower = [s.lower().strip() for s in jd_skills]
        
        cv_tools = [s for s in cv_skills_lower if any(t in s for t in tools_keywords)]
        jd_tools = [s for s in jd_skills_lower if any(t in s for t in tools_keywords)]
        
        if not jd_tools:
            return {'score': 100.0, 'matched_tools': []}
        
        matched_tools = []
        for cv_tool in cv_tools:
            for jd_tool in jd_tools:
                if cv_tool == jd_tool or cv_tool in jd_tool or jd_tool in cv_tool:
                    matched_tools.append(cv_tool)
                    break
        
        score = (len(matched_tools) / len(jd_tools)) * 100
        
        return {
            'score': score,
            'matched_tools': list(set(matched_tools))
        }
