
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class UnifiedJobScraper:
    """Unified scraper combining all job boards"""
    
    def __init__(self):
        self.scrapers = {
            'rozee': RozeeScraper(),
            'indeed': IndeedPakistanScraper(),
            'mustakbil': MustakbilScraper()
        }
        logger.info("✓ Unified scraper initialized")
    
    def scrape_all(self, keyword: str = "python", location: str = "karachi",
                   pages: int = 2) -> List[Dict]:
        """
        Scrape from all job boards
        
        Args:
            keyword: Job search keyword
            location: Job location
            pages: Number of pages per site
            
        Returns:
            List of unique jobs from all sources
        """
        all_jobs = []
        
        # Rozee.pk
        try:
            rozee_jobs = self.scrapers['rozee'].scrape_jobs(keyword, location, pages)
            all_jobs.extend(rozee_jobs)
        except Exception as e:
            logger.error(f"Rozee scraping failed: {e}")
        
        # Indeed.pk
        try:
            indeed_jobs = self.scrapers['indeed'].scrape_jobs(keyword, location, pages)
            all_jobs.extend(indeed_jobs)
        except Exception as e:
            logger.error(f"Indeed scraping failed: {e}")
        
        # Mustakbil.com
        try:
            mustakbil_jobs = self.scrapers['mustakbil'].scrape_jobs(keyword, pages)
            all_jobs.extend(mustakbil_jobs)
        except Exception as e:
            logger.error(f"Mustakbil scraping failed: {e}")
        
        # Remove duplicates
        unique_jobs = self._remove_duplicates(all_jobs)
        
        logger.info(f"✓ Total unique jobs scraped: {len(unique_jobs)}")
        return unique_jobs
    
    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title + company"""
        seen = set()
        unique = []
        
        for job in jobs:
            key = (
                job.get('job_title', '').lower(),
                job.get('company', '').lower()
            )
            
            if key not in seen and key != ('', ''):
                seen.add(key)
                unique.append(job)
        
        return unique


# Example usage
if __name__ == "__main__":
    scraper = UnifiedJobScraper()
    jobs = scraper.scrape_all(keyword="python developer", location="karachi", pages=2)
    
    print(f"\n✓ Scraped {len(jobs)} jobs")
    if jobs:
        print("\nSample job:")
        print(jobs[0])