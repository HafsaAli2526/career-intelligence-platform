import re
from typing import List, Optional

def clean_text(text: str) -> str:
    """
    Clean and normalize text
    - Remove extra whitespace
    - Strip leading/trailing spaces
    - Normalize line breaks
    """
    if not text:
        return ""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text

def extract_emails(text: str) -> List[str]:
    """
    Extract all email addresses from text
    """
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)

def extract_phones(text: str) -> List[str]:
    """
    Extract phone numbers (Pakistani formats)
    - +92 format: +92-3xx-xxxxxxx
    - Local format: 03xx-xxxxxxx
    - Landline: (0xx) xxx-xxxx
    """
    patterns = [
        r'\+92[-\s]?[0-9]{10}',  # +92 format
        r'0[0-9]{10}',            # Local 11-digit
        r'\([0-9]{3}\)[-\s]?[0-9]{7}',  # (0xx) format
        r'0[0-9]{2,3}[-\s]?[0-9]{7,8}'  # Landline
    ]
    
    phones = []
    for pattern in patterns:
        phones.extend(re.findall(pattern, text))
    
    return list(set(phones))  # Remove duplicates

def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(pattern, text)

def remove_special_characters(text: str, keep_spaces: bool = True) -> str:
    """
    Remove special characters from text
    Args:
        text: Input text
        keep_spaces: If True, preserve spaces
    """
    if keep_spaces:
        pattern = r'[^a-zA-Z0-9\s]'
    else:
        pattern = r'[^a-zA-Z0-9]'
    
    return re.sub(pattern, '', text)

def tokenize_text(text: str) -> List[str]:
    """
    Simple tokenization by splitting on whitespace
    """
    return text.split()

def extract_section_text(text: str, section_name: str) -> Optional[str]:
    """
    Extract text from a specific section (e.g., "Skills", "Experience")
    Args:
        text: Full document text
        section_name: Name of section to extract
    Returns:
        Section text or None if not found
    """
    # Pattern to match section headers
    pattern = rf'(?i){section_name}[\s:]*\n(.*?)(?:\n[A-Z][a-z]+[\s:]|\Z)'
    match = re.search(pattern, text, re.DOTALL)
    
    return match.group(1).strip() if match else None
