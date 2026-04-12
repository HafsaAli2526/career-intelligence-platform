from .core_routes import router as core_router
from .cv_routes import router as cv_router
from .jd_routes import router as jd_router
from .match_routes import router as match_router
from .scraper_routes import router as scraper_router

__all__ = [
    'core_router',
    'cv_router',
    'jd_router',
    'match_router',
    'scraper_router'
]