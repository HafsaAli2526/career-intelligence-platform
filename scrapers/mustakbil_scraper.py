from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MustakbilScraper:
    """Scraper for Mustakbil.com (requires Selenium)"""
    
    def __init__(self, delay: int = 2):
        self.base_url = "https://www.mustakbil.com"
        self.delay = delay
    
    def _setup_driver(self, headless: bool = True):
        """Setup Selenium WebDriver"""
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup driver: {e}")
            return None
    
    def scrape_jobs(self, keyword: str = "software", pages: int = 3) -> List[Dict]:
        """Scrape jobs from Mustakbil"""
        jobs = []
        driver = self._setup_driver()
        
        if not driver:
            logger.warning("Mustakbil scraper unavailable (Selenium required)")
            return jobs
        
        try:
            for page in range(1, pages + 1):
                logger.info(f"Scraping Mustakbil page {page}...")
                
                url = f"{self.base_url}/jobs/{keyword}?page={page}"
                driver.get(url)
                
                time.sleep(3)  # Wait for page load
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                job_cards = soup.find_all('div', class_='job-listing')
                
                for card in job_cards:
                    job_data = self._parse_job_card(card)
                    if job_data:
                        jobs.append(job_data)
                
                time.sleep(self.delay)
                
        except Exception as e:
            logger.error(f"Error scraping Mustakbil: {e}")
        finally:
            driver.quit()
        
        logger.info(f"✓ Scraped {len(jobs)} jobs from Mustakbil")
        return jobs
    
    def _parse_job_card(self, card) -> Optional[Dict]:
        """Parse Mustakbil job card"""
        try:
            title_elem = card.find('h3')
            job_title = title_elem.text.strip() if title_elem else None
            
            company_elem = card.find('div', class_='company-name')
            company = company_elem.text.strip() if company_elem else None
            
            location_elem = card.find('span', class_='location')
            location = location_elem.text.strip() if location_elem else None
            
            link_elem = card.find('a', href=True)
            job_url = f"{self.base_url}{link_elem['href']}" if link_elem else None
            
            return {
                'job_title': job_title,
                'company': company,
                'location': location,
                'raw_text': "",  # Would need additional request
                'source_url': job_url,
                'source_platform': 'mustakbil.com'
            }
            
        except Exception as e:
            logger.error(f"Error parsing Mustakbil job card: {e}")
            return None
