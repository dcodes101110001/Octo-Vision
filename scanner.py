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
            ValueError: If CSV parsing fails or is empty
        """
        # Check for empty content
        if not csv_content or not csv_content.strip():
            raise ValueError("CSV file is empty. Please upload a file with at least one keyword.")
        
        try:
            # Try to read CSV with pandas
            df = pd.read_csv(StringIO(csv_content))
            
            # Check if dataframe is empty
            if df.empty:
                raise ValueError("CSV file contains no data. Please add at least one keyword.")
            
            # Get keywords from first column
            if len(df.columns) > 0:
                keywords = df.iloc[:, 0].dropna().astype(str).tolist()
                self.keywords = [k.strip() for k in keywords if k.strip()]
                
                # Check if we got any valid keywords after cleaning
                if not self.keywords:
                    raise ValueError("CSV file contains no valid keywords. Please check your file format.")
                
                return self.keywords
            
            raise ValueError("CSV file has no columns. Please check your file format.")
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty or has no data. Please upload a file with at least one keyword.") from None
        except pd.errors.ParserError as e:
            raise ValueError(f"CSV file format is invalid: {str(e)}") from e
        except ValueError:
            # Re-raise ValueError as-is (our custom messages)
            raise
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
                'total_occurrences': 0,
                'match_details': []
            }
        
        matched_keywords = set()
        match_details = []
        total_occurrences = 0
        
        for keyword in self.keywords:
            # Try regex pattern matching
            try:
                # Use IGNORECASE flag if not case sensitive to ensure correct positions
                flags = 0 if self.case_sensitive else re.IGNORECASE
                pattern = re.compile(re.escape(keyword), flags)
                matches = list(pattern.finditer(text))
                
                if matches:
                    matched_keywords.add(keyword)
                    total_occurrences += len(matches)
                    
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
                        # Count all occurrences in fallback mode
                        count = text.count(keyword)
                        total_occurrences += count
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
                        # Count all occurrences in fallback mode
                        count = text_lower.count(search_keyword)
                        total_occurrences += count
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
            'total_occurrences': total_occurrences,
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
            # Skip entries that have errors (no content)
            if 'error' in text_info or not text_info.get('content'):
                continue
                
            content = text_info.get('content', '')
            scan_result = self.scan_text(content)
            
            if scan_result['matches_found']:
                results.append({
                    **text_info,
                    **scan_result
                })
        
        return results
