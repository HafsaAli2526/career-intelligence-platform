
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class IndeedPakistanScraper:
    """Scraper for Indeed.pk"""
    
    def __init__(self, delay: int = 2):
        self.base_url = "https://pk.indeed.com"
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_jobs(self, keyword: str = "python developer", 
                   location: str = "Karachi", pages: int = 3) -> List[Dict]:
        """Scrape jobs from Indeed Pakistan"""
        jobs = []
        
        for page_num in range(pages):
            start = page_num * 10
            logger.info(f"Scraping Indeed.pk page {page_num + 1}...")
            
            url = f"{self.base_url}/jobs?q={keyword}&l={location}&start={start}"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards:
                    job_data = self._parse_job_card(card)
                    if job_data:
                        jobs.append(job_data)
                
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error scraping Indeed page {page_num}: {e}")
        
        logger.info(f"✓ Scraped {len(jobs)} jobs from Indeed.pk")
        return jobs
    
    def _parse_job_card(self, card) -> Optional[Dict]:
        """Parse Indeed job card"""
        try:
            title_elem = card.find('h2', class_='jobTitle')
            job_title = title_elem.text.strip() if title_elem else None
            
            company_elem = card.find('span', class_='companyName')
            company = company_elem.text.strip() if company_elem else None
            
            location_elem = card.find('div', class_='companyLocation')
            location = location_elem.text.strip() if location_elem else None
            
            snippet_elem = card.find('div', class_='job-snippet')
            description = snippet_elem.text.strip() if snippet_elem else ""
            
            salary_elem = card.find('span', class_='salary-snippet')
            salary_text = salary_elem.text.strip() if salary_elem else None
            
            link_elem = card.find('a', class_='jcs-JobTitle')
            job_url = f"{self.base_url}{link_elem['href']}" if link_elem else None
            
            return {
                'job_title': job_title,
                'company': company,
                'location': location,
                'raw_text': description,
                'salary_text': salary_text,
                'source_url': job_url,
                'source_platform': 'indeed.pk'
            }
            
        except Exception as e:
            logger.error(f"Error parsing Indeed job card: {e}")
            return None