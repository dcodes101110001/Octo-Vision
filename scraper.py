"""
Paste Site Scraper Module
Handles scraping of paste sites like Pastebin
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time


class PasteScraper:
    """Scraper for paste sites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_pastebin_recent(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        Scrape recent public pastes from Pastebin
        
        Args:
            limit: Maximum number of pastes to retrieve
            
        Returns:
            List of dictionaries containing paste information
        """
        pastes = []
        
        try:
            # Pastebin archive page
            url = "https://pastebin.com/archive"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find paste links in the archive
            paste_rows = soup.find_all('tr', class_='data')
            
            for row in paste_rows[:limit]:
                try:
                    link_tag = row.find('a')
                    if link_tag:
                        paste_id = link_tag['href'].strip('/')
                        title = link_tag.text.strip() or "Untitled"
                        
                        # Get the raw paste content
                        raw_url = f"https://pastebin.com/raw/{paste_id}"
                        time.sleep(0.5)  # Rate limiting
                        
                        raw_response = self.session.get(raw_url, timeout=10)
                        if raw_response.status_code == 200:
                            content = raw_response.text
                            
                            pastes.append({
                                'id': paste_id,
                                'title': title,
                                'content': content,
                                'url': f"https://pastebin.com/{paste_id}"
                            })
                except Exception as e:
                    pastes.append({
                        'id': None,
                        'title': 'Error',
                        'content': '',
                        'url': link_tag['href'] if 'link_tag' in locals() and link_tag else None,
                        'error': str(e)
                    })
                    continue
                    
        except Exception as e:
            pastes.append({
                'id': '',
                'title': 'Error accessing Pastebin',
                'content': '',
                'url': '',
                'error': str(e)
            })
        
        return pastes
    
    def scrape_custom_paste(self, url: str) -> Dict[str, str]:
        """
        Scrape a specific paste URL
        
        Args:
            url: URL of the paste to scrape
            
        Returns:
            Dictionary containing paste information
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # If it's a raw URL, return content directly
            if '/raw/' in url:
                return {
                    'url': url,
                    'content': response.text,
                    'title': 'Custom Paste'
                }
            
            # Otherwise parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract paste content (this is generic and may need adjustment)
            content_div = soup.find('textarea') or soup.find('pre') or soup.find('code')
            
            if content_div:
                content = content_div.get_text()
            else:
                content = soup.get_text()
            
            return {
                'url': url,
                'content': content,
                'title': 'Custom Paste'
            }
            
        except Exception as e:
            return {
                'url': url,
                'content': '',
                'error': str(e),
                'title': 'Error'
            }
