"""
Keyword Scanner Module
Handles pattern matching and keyword detection
"""

import re
from typing import List, Dict
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
        """
        try:
            # Try to read CSV with pandas
            df = pd.read_csv(StringIO(csv_content))
            
            # Get keywords from first column
            if len(df.columns) > 0:
                keywords = df.iloc[:, 0].dropna().astype(str).tolist()
                self.keywords = [k.strip() for k in keywords if k.strip()]
                return self.keywords
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return []
    
    def load_keywords_from_list(self, keywords: List[str]):
        """
        Load keywords from a list
        
        Args:
            keywords: List of keyword strings
        """
        self.keywords = [k.strip() for k in keywords if k.strip()]
    
    def scan_text(self, text: str) -> Dict[str, any]:
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
        
        search_text = text if self.case_sensitive else text.lower()
        
        for keyword in self.keywords:
            search_keyword = keyword if self.case_sensitive else keyword.lower()
            
            # Try regex pattern matching
            try:
                pattern = re.compile(re.escape(search_keyword), 
                                   re.IGNORECASE if not self.case_sensitive else 0)
                matches = list(pattern.finditer(search_text))
                
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
            except Exception as e:
                # Fallback to simple string search
                if search_keyword in search_text:
                    matched_keywords.add(keyword)
                    index = search_text.find(search_keyword)
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
    
    def scan_multiple_texts(self, texts: List[Dict[str, str]]) -> List[Dict[str, any]]:
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
