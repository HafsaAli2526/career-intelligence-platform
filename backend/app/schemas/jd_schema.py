from pydantic import BaseModel
from typing import List, Optional, Dict

# === Matching Schemas ===

class MatchResult(BaseModel):
    """Individual match result"""
    rank: int
    jd_id: int
    jd_title: str
    company: str
    location: str
    semantic_score: float
    skill_overlap_score: float
    title_match_score: float
    final_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    salary_info: Dict

class MatchResponse(BaseModel):
    """CV-JD matching response"""
    status: str
    cv_id: int
    total_jobs_analyzed: int
    top_matches: List[MatchResult]


# === ATS Score Schemas ===

class ATSScoreResponse(BaseModel):
    """ATS scoring response"""
    status: str
    ats_score_id: int
    result: Dict
    # Result contains:
    # - ats_score: float (0-100)
    # - skill_match_score: float
    # - title_alignment: float
    # - experience_score: float
    # - education_score: float
    # - tools_match_score: float
    # - common_skills: List[str]
    # - missing_skills: List[str]
    # - title_match: bool
    # - experience_match: bool
    # - education_match: bool
    # - years_required: int
    # - years_achieved: int
    # - breakdown: Dict


# === Skill Gap Schemas ===

class SkillGapResponse(BaseModel):
    """Skill gap analysis response"""
    status: str
    gap_id: int
    result: Dict
    # Result contains:
    # - missing_technical_skills: List[str]
    # - missing_soft_skills: List[str]
    # - categorized_gaps: Dict
    # - priority_skills: List[str]
    # - gap_severity: str (low/medium/high)
    # - total_missing: int
    # - match_percentage: float


# === RAG Recommendation Schemas ===

class CourseRecommendation(BaseModel):
    """Single course recommendation"""
    skill: str
    course_title: str
    provider: str
    duration: str
    level: str
    url: str
    description: Optional[str] = None

class RecommendationResponse(BaseModel):
    """RAG recommendation response"""
    status: str
    recommendations: List[Dict]
    courses: List[Dict]
    missing_skills: List[str]
    roadmap: str
    metadata: Dict


# === Analytics Schemas ===

class SalaryStatsResponse(BaseModel):
    """Salary statistics response"""
    job_title: str
    location: Optional[str]
    min_salary: int
    max_salary: int
    avg_salary: int
    median_salary: Optional[int]
    sample_count: int
    currency: str = "PKR"

class TrendingSkillsResponse(BaseModel):
    """Trending skills response"""
    trending_skills: List[Dict]  # [{"skill": str, "demand_count": int}]
    total_unique_skills: int