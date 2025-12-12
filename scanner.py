"""
Keyword Scanner Module
Handles pattern matching and keyword detection
"""

import re
from typing import List, Dict, Any
import pandas as pd
from io import StringIO


class KeywordScanner:
    """Scanner for detecting keywords and patterns in text"""
    
    def __init__(self, keywords: List[str] = None, case_sensitive: bool = False):
        """
        Initialize the scanner with keywords
        
        Args:
            keywords: List of keywords or patterns to search for
            case_sensitive: Whether the search should be case-sensitive
        """
        self.keywords = keywords or []
        self.case_sensitive = case_sensitive
    
    def load_keywords_from_csv(self, csv_content: str) -> List[str]:
        """
        Load keywords from CSV content
        
        Args:
            csv_content: CSV file content as string
            
        Returns:
            List of keywords
            
        Raises:
            ValueError: If CSV parsing fails
        """
        try:
            # Try to read CSV with pandas
            df = pd.read_csv(StringIO(csv_content))
            
            # Get keywords from first column
            if len(df.columns) > 0:
                keywords = df.iloc[:, 0].dropna().astype(str).tolist()
                self.keywords = [k.strip() for k in keywords if k.strip()]
                return self.keywords
            
            return []
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}") from e
    
    def load_keywords_from_list(self, keywords: List[str]):
        """
        Load keywords from a list
        
        Args:
            keywords: List of keyword strings
        """
        self.keywords = [k.strip() for k in keywords if k.strip()]
    
    def scan_text(self, text: str) -> Dict[str, Any]:
        """
        Scan text for keywords and return matches
        
        Args:
            text: Text to scan
            
        Returns:
            Dictionary with scan results
        """
        if not text or not self.keywords:
            return {
                'matches_found': False,
                'matched_keywords': [],
                'match_count': 0,
                'match_details': []
            }
        
        matched_keywords = set()
        match_details = []
        
        for keyword in self.keywords:
            # Try regex pattern matching
            try:
                # Use IGNORECASE flag if not case sensitive to ensure correct positions
                flags = 0 if self.case_sensitive else re.IGNORECASE
                pattern = re.compile(re.escape(keyword), flags)
                matches = list(pattern.finditer(text))
                
                if matches:
                    matched_keywords.add(keyword)
                    
                    # Get context around matches (50 chars before and after)
                    for match in matches[:3]:  # Limit to first 3 occurrences per keyword
                        start = max(0, match.start() - 50)
                        end = min(len(text), match.end() + 50)
                        context = text[start:end].replace('\n', ' ').strip()
                        
                        match_details.append({
                            'keyword': keyword,
                            'position': match.start(),
                            'context': f"...{context}..."
                        })
            except Exception:
                # Fallback to simple string search with manual case handling
                if self.case_sensitive:
                    if keyword in text:
                        matched_keywords.add(keyword)
                        index = text.find(keyword)
                        start = max(0, index - 50)
                        end = min(len(text), index + len(keyword) + 50)
                        context = text[start:end].replace('\n', ' ').strip()
                        
                        match_details.append({
                            'keyword': keyword,
                            'position': index,
                            'context': f"...{context}..."
                        })
                else:
                    # For case-insensitive, manually search for positions in original text
                    search_keyword = keyword.lower()
                    text_lower = text.lower()
                    
                    if search_keyword in text_lower:
                        matched_keywords.add(keyword)
                        index = text_lower.find(search_keyword)
                        start = max(0, index - 50)
                        end = min(len(text), index + len(keyword) + 50)
                        context = text[start:end].replace('\n', ' ').strip()
                        
                        match_details.append({
                            'keyword': keyword,
                            'position': index,
                            'context': f"...{context}..."
                        })
        
        return {
            'matches_found': len(matched_keywords) > 0,
            'matched_keywords': sorted(list(matched_keywords)),
            'match_count': len(matched_keywords),
            'match_details': match_details
        }
    
    def scan_multiple_texts(self, texts: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Scan multiple texts for keywords
        
        Args:
            texts: List of dictionaries containing text information
            
        Returns:
            List of scan results for each text
        """
        results = []
        
        for text_info in texts:
            content = text_info.get('content', '')
            scan_result = self.scan_text(content)
            
            if scan_result['matches_found']:
                results.append({
                    **text_info,
                    **scan_result
                })
        
        return results
