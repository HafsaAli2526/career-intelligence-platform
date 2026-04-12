
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from difflib import SequenceMatcher
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class JobMatcher:
    """
    CV-JD Matching Engine
    Matches CVs with Job Descriptions using:
    - Semantic similarity (60%)
    - Skill overlap (30%)
    - Title matching (10%)
    """
    
    def __init__(self):
        self.weights = {
            'semantic': settings.MATCH_WEIGHT_SEMANTIC,  # 0.60
            'skill': settings.MATCH_WEIGHT_SKILLS,       # 0.30
            'title': settings.MATCH_WEIGHT_TITLE         # 0.10
        }
        logger.info(f"Matcher initialized with weights: {self.weights}")
    
    def match_cv_with_jds(self, cv_data: Dict, jd_list: List[Dict], 
                          top_k: int = 10) -> List[Dict]:
        """
        Match CV against multiple JDs
        
        Args:
            cv_data: Parsed CV data with embedding
            jd_list: List of parsed JD data with embeddings
            top_k: Number of top matches to return
            
        Returns:
            List of top K matches with scores
        """
        logger.info(f"Matching CV against {len(jd_list)} jobs")
        matches = []
        
        for jd in jd_list:
            match_result = self.compute_match_score(cv_data, jd)
            matches.append({
                'jd_id': jd.get('id'),
                'jd_title': jd.get('job_title'),
                'company': jd.get('company'),
                'location': jd.get('location'),
                'semantic_score': match_result['semantic_score'],
                'skill_overlap_score': match_result['skill_overlap_score'],
                'title_match_score': match_result['title_match_score'],
                'final_score': match_result['final_score'],
                'matching_skills': match_result['matching_skills'],
                'missing_skills': match_result['missing_skills'],
                'salary_info': {
                    'min': jd.get('salary_min'),
                    'max': jd.get('salary_max'),
                    'text': jd.get('salary_text'),
                    'currency': jd.get('salary_currency', 'PKR')
                }
            })
        
        # Sort by final score
        matches.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Add rank
        for idx, match in enumerate(matches[:top_k], 1):
            match['rank'] = idx
        
        logger.info(f"✓ Top {top_k} matches computed")
        return matches[:top_k]
    
    def compute_match_score(self, cv_data: Dict, jd_data: Dict) -> Dict:
        """Compute matching score between CV and JD"""
        
        # 1. Semantic Similarity (embeddings)
        semantic_score = self._compute_semantic_similarity(
            cv_data.get('embedding', []),
            jd_data.get('embedding', [])
        )
        
        # 2. Skill Overlap
        skill_result = self._compute_skill_overlap(
            cv_data.get('skills', []),
            jd_data.get('required_skills', [])
        )
        
        # 3. Title Match
        title_match_score = self._compute_title_match(
            cv_data.get('job_title'),
            jd_data.get('job_title')
        )
        
        # 4. Final Score (weighted)
        final_score = (
            self.weights['semantic'] * semantic_score +
            self.weights['skill'] * skill_result['score'] +
            self.weights['title'] * title_match_score
        )
        
        return {
            'semantic_score': round(semantic_score, 3),
            'skill_overlap_score': round(skill_result['score'], 3),
            'title_match_score': round(title_match_score, 3),
            'final_score': round(final_score, 3),
            'matching_skills': skill_result['matching'],
            'missing_skills': skill_result['missing']
        }
    
    def _compute_semantic_similarity(self, cv_embedding: List[float], 
                                    jd_embedding: List[float]) -> float:
        """Cosine similarity between embeddings"""
        if not cv_embedding or not jd_embedding:
            return 0.0
        
        cv_vec = np.array(cv_embedding).reshape(1, -1)
        jd_vec = np.array(jd_embedding).reshape(1, -1)
        
        similarity = cosine_similarity(cv_vec, jd_vec)[0][0]
        return max(0.0, min(1.0, similarity))
    
    def _compute_skill_overlap(self, cv_skills: List[str], 
                               jd_skills: List[str]) -> Dict:
        """Compute skill overlap score"""
        if not jd_skills:
            return {'score': 0.0, 'matching': [], 'missing': []}
        
        cv_skills_set = set(s.lower() for s in cv_skills)
        jd_skills_set = set(s.lower() for s in jd_skills)
        
        matching_skills = cv_skills_set.intersection(jd_skills_set)
        missing_skills = jd_skills_set - cv_skills_set
        
        score = len(matching_skills) / len(jd_skills_set)
        
        return {
            'score': score,
            'matching': sorted(list(matching_skills)),
            'missing': sorted(list(missing_skills))
        }
    
    def _compute_title_match(self, cv_title: str, jd_title: str) -> float:
        """Compare job titles using string similarity"""
        if not cv_title or not jd_title:
            return 0.0
        
        cv_title = cv_title.lower().strip()
        jd_title = jd_title.lower().strip()
        
        if cv_title == jd_title:
            return 1.0
        
        similarity = SequenceMatcher(None, cv_title, jd_title).ratio()
        
        # Keyword bonus
        keywords = ['developer', 'engineer', 'analyst', 'manager', 'designer']
        cv_keywords = set(kw for kw in keywords if kw in cv_title)
        jd_keywords = set(kw for kw in keywords if kw in jd_title)
        keyword_overlap = len(cv_keywords.intersection(jd_keywords))
        
        return min(1.0, (similarity * 0.7) + (keyword_overlap * 0.1))
