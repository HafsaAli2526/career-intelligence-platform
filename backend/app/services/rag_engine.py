
import os
from typing import List, Dict, Optional
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatAnthropic, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class RAGRecommendationEngine:
    """
    RAG-based Recommendation System
    Sources: Coursera, DigiSkills, YouTube, Local Pakistani academies
    Uses: LangChain + ChromaDB + LLM (GPT/Claude/Llama)
    """
    
    def __init__(self, llm_provider: str = "anthropic"):
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.SENTENCE_TRANSFORMER_MODEL
        )
        
        # Initialize vector store
        try:
            self.vector_store = Chroma(
                persist_directory=settings.CHROMA_DB_PATH,
                embedding_function=self.embeddings,
                collection_name="courses"
            )
            logger.info("✓ ChromaDB initialized")
        except Exception as e:
            logger.warning(f"ChromaDB initialization failed: {e}")
            self.vector_store = None
        
        # Initialize LLM
        self.llm = self._init_llm(llm_provider)
        
        # Create QA chain
        if self.vector_store and self.llm:
            self.qa_chain = self._create_qa_chain()
        else:
            self.qa_chain = None
    
    def _init_llm(self, provider: str):
        """Initialize LLM based on provider"""
        try:
            if provider == "anthropic" and settings.ANTHROPIC_API_KEY:
                return ChatAnthropic(
                    model="claude-3-sonnet-20240229",
                    anthropic_api_key=settings.ANTHROPIC_API_KEY,
                    temperature=0.7
                )
            elif provider == "openai" and settings.OPENAI_API_KEY:
                return ChatOpenAI(
                    model="gpt-4",
                    openai_api_key=settings.OPENAI_API_KEY,
                    temperature=0.7
                )
            else:
                logger.warning("No LLM API key configured")
                return None
        except Exception as e:
            logger.error(f"LLM initialization failed: {e}")
            return None
    
    def _create_qa_chain(self):
        """Create RetrievalQA chain"""
        template = """You are a career development advisor for Pakistani professionals.

Based on the course information below, create a personalized learning roadmap.

Course Database Context:
{context}

Missing Skills: {question}

Provide:
1. Recommended courses (include provider, duration, level)
2. Learning sequence (what to learn first, second, etc.)
3. Estimated total time to acquire these skills
4. Practical tips for Pakistani learners
5. Free resources where possible (DigiSkills, YouTube)

Format your response clearly with course names, providers, and links.
"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        try:
            chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_kwargs={"k": settings.RAG_TOP_K}
                ),
                chain_type_kwargs={"prompt": prompt}
            )
            return chain
        except Exception as e:
            logger.error(f"QA chain creation failed: {e}")
            return None
    
    def generate_recommendations(self, missing_skills: List[str],
                                cv_data: Dict = None,
                                jd_data: Dict = None) -> Dict:
        """
        Generate personalized learning recommendations
        
        Args:
            missing_skills: List of skills to learn
            cv_data: Optional CV context
            jd_data: Optional JD context
            
        Returns:
            Recommendations with courses and roadmap
        """
        if not missing_skills:
            return {
                'recommendations': [],
                'courses': [],
                'missing_skills': [],
                'roadmap': "No skill gaps identified!",
                'metadata': {'skill_count': 0, 'courses_found': 0}
            }
        
        logger.info(f"Generating recommendations for {len(missing_skills)} skills")
        
        # Build query
        query = self._build_query(missing_skills, cv_data, jd_data)
        
        # Get recommendations
        if self.qa_chain:
            try:
                response = self.qa_chain.run(query)
                roadmap = response
            except Exception as e:
                logger.error(f"RAG query failed: {e}")
                roadmap = self._generate_fallback_roadmap(missing_skills)
        else:
            roadmap = self._generate_fallback_roadmap(missing_skills)
        
        # Retrieve courses
        courses = self._retrieve_courses(missing_skills)
        
        # Structure recommendations
        recommendations = self._structure_recommendations(missing_skills)
        
        return {
            'recommendations': recommendations,
            'courses': courses,
            'missing_skills': missing_skills,
            'roadmap': roadmap,
            'metadata': {
                'skill_count': len(missing_skills),
                'courses_found': len(courses)
            }
        }
    
    def _build_query(self, missing_skills: List[str], cv_data: Dict, jd_data: Dict) -> str:
        """Build query for LLM"""
        query = f"I need to learn: {', '.join(missing_skills)}. "
        
        if cv_data:
            current_skills = cv_data.get('skills', [])[:5]
            if current_skills:
                query += f"I currently know: {', '.join(current_skills)}. "
        
        if jd_data:
            job_title = jd_data.get('job_title')
            if job_title:
                query += f"Target role: {job_title}. "
        
        query += "Recommend a learning path."
        return query
    
    def _generate_fallback_roadmap(self, missing_skills: List[str]) -> str:
        """Generate fallback roadmap when LLM unavailable"""
        return f"""Learning Roadmap:

Priority Skills: {', '.join(missing_skills[:3])}

Recommended Approach:
1. Start with foundational skills: {missing_skills[0] if missing_skills else 'N/A'}
2. Practice through projects
3. Estimated time: 2-3 months with consistent effort

Resources:
- Coursera, Udemy for structured courses
- DigiSkills.pk for free Pakistani courses
- YouTube for tutorials
"""
    
    def _retrieve_courses(self, skills: List[str]) -> List[Dict]:
        """Retrieve relevant courses from vector store"""
        courses = []
        
        if not self.vector_store:
            return self._get_default_courses(skills)
        
        try:
            for skill in skills[:5]:
                results = self.vector_store.similarity_search(skill, k=2)
                for doc in results:
                    courses.append({
                        'title': doc.metadata.get('title', 'N/A'),
                        'provider': doc.metadata.get('provider', 'N/A'),
                        'url': doc.metadata.get('url', '#'),
                        'duration': doc.metadata.get('duration', 'N/A'),
                        'level': doc.metadata.get('level', 'N/A'),
                        'skill': skill
                    })
        except Exception as e:
            logger.error(f"Course retrieval failed: {e}")
            return self._get_default_courses(skills)
        
        return courses
    
    def _get_default_courses(self, skills: List[str]) -> List[Dict]:
        """Default course recommendations"""
        default_courses = {
            'python': {'title': 'Python for Everybody', 'provider': 'Coursera', 'url': 'https://coursera.org'},
            'javascript': {'title': 'JavaScript Complete Course', 'provider': 'Udemy', 'url': 'https://udemy.com'},
            'react': {'title': 'React - The Complete Guide', 'provider': 'Udemy', 'url': 'https://udemy.com'},
        }
        
        courses = []
        for skill in skills[:5]:
            if skill in default_courses:
                course = default_courses[skill].copy()
                course['skill'] = skill
                course['duration'] = '40 hours'
                course['level'] = 'intermediate'
                courses.append(course)
        
        return courses
    
    def _structure_recommendations(self, missing_skills: List[str]) -> List[Dict]:
        """Structure recommendations"""
        return [
            {
                'skill': skill,
                'priority': 'high' if i < 3 else 'medium',
                'estimated_time': '20-40 hours',
                'category': self._categorize_skill(skill)
            }
            for i, skill in enumerate(missing_skills)
        ]
    
    def _categorize_skill(self, skill: str) -> str:
        """Categorize skill"""
        categories = {
            'programming': ['python', 'java', 'javascript'],
            'web': ['react', 'angular', 'vue'],
            'cloud': ['aws', 'azure', 'docker'],
        }
        
        skill_lower = skill.lower()
        for category, keywords in categories.items():
            if any(kw in skill_lower for kw in keywords):
                return category
        return 'other'
    
    def add_courses_to_vector_store(self, courses: List[Dict]):
        """Add course data to vector store"""
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return
        
        documents = []
        for course in courses:
            text = f"{course['title']}. {course.get('description', '')}. Skills: {', '.join(course.get('skills_covered', []))}"
            doc = Document(
                page_content=text,
                metadata={
                    'title': course['title'],
                    'provider': course.get('provider', 'Unknown'),
                    'url': course.get('url', '#'),
                    'duration': course.get('duration_hours', 'N/A'),
                    'level': course.get('level', 'beginner')
                }
            )
            documents.append(doc)
        
        try:
            self.vector_store.add_documents(documents)
            self.vector_store.persist()
            logger.info(f"✓ Added {len(courses)} courses to vector store")
        except Exception as e:
            logger.error(f"Failed to add courses: {e}")

