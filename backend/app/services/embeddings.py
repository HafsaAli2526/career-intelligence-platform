
from sentence_transformers import SentenceTransformer
from typing import List, Union, Dict
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Generate embeddings using Sentence-BERT (MiniLM)
    For semantic similarity in matching
    """
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"✓ Embedding model loaded: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.model = None
    
    def generate_embedding(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Generate embedding(s) for text"""
        if not self.model:
            return []
        
        embeddings = self.model.encode(text)
        
        if isinstance(text, str):
            return embeddings.tolist()
        else:
            return [emb.tolist() for emb in embeddings]
    
    def generate_cv_embedding(self, cv_data: Dict) -> List[float]:
        """Generate embedding specifically for CV"""
        text = f"{cv_data.get('job_title', '')} "
        text += f"{' '.join(cv_data.get('skills', []))} "
        text += f"{cv_data.get('summary', '')}"
        
        return self.generate_embedding(text)
    
    def generate_jd_embedding(self, jd_data: Dict) -> List[float]:
        """Generate embedding specifically for JD"""
        text = f"{jd_data.get('job_title', '')} "
        text += f"{' '.join(jd_data.get('required_skills', []))} "
        text += f"{' '.join(jd_data.get('responsibilities', [])[:3])}"
        
        return self.generate_embedding(text)
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity"""
        if not embedding1 or not embedding2:
            return 0.0
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)