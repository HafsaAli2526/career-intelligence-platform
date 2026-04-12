
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RozeeScraper:
    """Scraper for Rozee.pk"""
    
    def __init__(self, delay: int = 2):
        self.base_url = "https://www.rozee.pk"
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_jobs(self, keyword: str = "python", location: str = "karachi", 
                   pages: int = 3) -> List[Dict]:
        """Scrape jobs from Rozee.pk"""
        jobs = []
        
        for page in range(1, pages + 1):
            logger.info(f"Scraping Rozee.pk page {page}...")
            
            url = f"{self.base_url}/job/jsearch/q/{keyword}/l/{location}/fpn/{page}"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('div', class_='job')
                
                for card in job_cards:
                    job_data = self._parse_job_card(card)
                    if job_data:
                        jobs.append(job_data)
                
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error scraping Rozee page {page}: {e}")
        
        logger.info(f"✓ Scraped {len(jobs)} jobs from Rozee.pk")
        return jobs
    
    def _parse_job_card(self, card) -> Optional[Dict]:
        """Parse individual job card"""
        try:
            title_elem = card.find('h3', class_='title')
            job_title = title_elem.text.strip() if title_elem else None
            
            company_elem = card.find('div', class_='company')
            company = company_elem.text.strip() if company_elem else None
            
            location_elem = card.find('div', class_='location')
            location = location_elem.text.strip() if location_elem else None
            
            link_elem = card.find('a', href=True)
            job_url = f"{self.base_url}{link_elem['href']}" if link_elem else None
            
            # Get full description
            description = self._get_job_details(job_url) if job_url else ""
            
            return {
                'job_title': job_title,
                'company': company,
                'location': location,
                'raw_text': description,
                'source_url': job_url,
                'source_platform': 'rozee.pk'
            }
            
        except Exception as e:
            logger.error(f"Error parsing Rozee job card: {e}")
            return None
    
    def _get_job_details(self, url: str) -> str:
        """Get full job description"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            desc_elem = soup.find('div', class_='job-description')
            description = desc_elem.text.strip() if desc_elem else ""
            
            time.sleep(self.delay)
            return description
            
        except Exception as e:
            logger.error(f"Error getting Rozee job details: {e}")
            return ""

