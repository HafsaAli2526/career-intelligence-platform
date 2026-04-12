import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Application Settings
    All environment variables loaded from .env file
    """
    
    # Application
    APP_NAME: str = "AI-Powered Career Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://career_user:password@localhost:5432/career_platform"
    )
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Vector Database
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./vector_store/chroma_db")
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "./vector_store/faiss")
    
    # NLP Models
    SPACY_MODEL: str = "en_core_web_lg"
    SENTENCE_TRANSFORMER_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Scraping
    USER_AGENT: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    SCRAPING_DELAY: int = int(os.getenv("SCRAPING_DELAY", "2"))
    MAX_SCRAPE_PAGES: int = int(os.getenv("MAX_SCRAPE_PAGES", "5"))
    
    # Upload Settings
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".doc"]
    UPLOAD_DIR: str = "uploads/cvs"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS
    CORS_ORIGINS: list = ["*"]  # In production, specify exact origins
    
    # RAG Settings
    RAG_TOP_K: int = 5  # Number of similar documents to retrieve
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50
    
    # Matching Settings
    MATCHING_TOP_K: int = 10  # Default number of top matches
    
    # ATS Scoring Weights
    ATS_WEIGHT_SKILLS: float = 0.40
    ATS_WEIGHT_TITLE: float = 0.25
    ATS_WEIGHT_EXPERIENCE: float = 0.15
    ATS_WEIGHT_EDUCATION: float = 0.10
    ATS_WEIGHT_TOOLS: float = 0.10
    
    # Matching Weights
    MATCH_WEIGHT_SEMANTIC: float = 0.60
    MATCH_WEIGHT_SKILLS: float = 0.30
    MATCH_WEIGHT_TITLE: float = 0.10
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
