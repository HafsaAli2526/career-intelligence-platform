import re
from typing import Dict, Optional

class SalaryExtractor:
    """
    Extract salary information from text
    Handles Pakistani salary formats:
    - Rs 80,000 - 120,000
    - PKR 80000-120000
    - 80k - 100k
    - Competitive salary
    """
    
    def __init__(self):
        # Salary patterns (ordered by specificity)
        self.patterns = [
            # Rs 80,000 - 120,000 or PKR 80,000 - 120,000
            r'(?:Rs\.?|PKR)\s*(\d{1,3}(?:,\d{3})*)\s*[-–to]\s*(?:Rs\.?|PKR)?\s*(\d{1,3}(?:,\d{3})*)',
            
            # 80k - 100k or 80K-100K
            r'(\d{1,3})k\s*[-–to]\s*(\d{1,3})k',
            
            # Rs 100,000 or PKR 100000 (single value)
            r'(?:Rs\.?|PKR)\s*(\d{1,3}(?:,\d{3})*)',
            
            # Salary: 80000-120000
            r'salary[\s:]+(\d{1,3}(?:,\d{3})*)\s*[-–]\s*(\d{1,3}(?:,\d{3})*)',
            
            # 80-100k per month
            r'(\d{1,3})\s*[-–]\s*(\d{1,3})k\s*(?:per month|monthly|/month)',
            
            # Lakh notation: 1-2 lakh
            r'(\d+)\s*[-–]\s*(\d+)\s*(?:lakh|lac)',
        ]
        
        # Special phrases
        self.special_phrases = [
            'competitive salary',
            'market competitive',
            'above market rate',
            'attractive package',
            'as per industry standards',
            'negotiable',
            'competitive package',
            'market rate',
            'best in industry'
        ]
    
    def extract(self, text: str) -> Dict:
        """
        Extract salary from text
        
        Returns:
            Dict with keys: min, max, currency, text
        """
        salary_info = {
            'min': None,
            'max': None,
            'currency': 'PKR',
            'text': None
        }
        
        text_lower = text.lower()
        
        # Try each pattern
        for pattern in self.patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                # Check for lakh notation
                if 'lakh' in pattern or 'lac' in pattern:
                    if len(groups) >= 2:
                        salary_info['min'] = int(groups[0]) * 100000
                        salary_info['max'] = int(groups[1]) * 100000
                        salary_info['text'] = match.group(0)
                
                # Range found (two values)
                elif len(groups) >= 2 and groups[1]:
                    min_sal = self._normalize_salary(groups[0])
                    max_sal = self._normalize_salary(groups[1])
                    
                    salary_info['min'] = min_sal
                    salary_info['max'] = max_sal
                    salary_info['text'] = match.group(0)
                
                # Single value
                elif len(groups) >= 1:
                    sal = self._normalize_salary(groups[0])
                    salary_info['min'] = sal
                    salary_info['max'] = sal
                    salary_info['text'] = match.group(0)
                
                break
        
        # Check for special phrases if no numeric salary found
        if not salary_info['text']:
            for phrase in self.special_phrases:
                if phrase in text_lower:
                    salary_info['text'] = phrase
                    break
        
        return salary_info
    
    def _normalize_salary(self, salary_str: str) -> int:
        """
        Convert salary string to integer
        Handles: commas, 'k' notation
        """
        # Remove commas
        salary_str = salary_str.replace(',', '').strip()
        
        # Handle 'k' notation (thousands)
        if 'k' in salary_str.lower():
            return int(float(salary_str.lower().replace('k', '')) * 1000)
        
        try:
            return int(salary_str)
        except ValueError:
            return 0