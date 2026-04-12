from typing import List, Dict
import sys
from pathlib import Path

# Add scrapers directory to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'scrapers'))

try:
    from scrapers.job_scrapers import UnifiedJobScraper as ExternalScraper
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    logger.warning("External scrapers not available")

import logging
logger = logging.getLogger(__name__)

class UnifiedJobScraper:
    """
    Unified Job Scraper
    Wrapper for external scraper modules
    """
    
    def __init__(self):
        if SCRAPER_AVAILABLE:
            self.scraper = ExternalScraper()
            logger.info("✓ Unified scraper initialized")
        else:
            self.scraper = None
            logger.warning("⚠ Scraper not available")
    
    def scrape_all(self, keyword: str = "python", 
                   location: str = "karachi",
                   pages: int = 2) -> List[Dict]:
        """
        Scrape from all job boards
        
        Returns list of raw job data
        """
        if not self.scraper:
            logger.error("Scraper not initialized")
            return []
        
        try:
            jobs = self.scraper.scrape_all(keyword, location, pages)
            logger.info(f"✓ Scraped {len(jobs)} jobs")
            return jobs
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return []