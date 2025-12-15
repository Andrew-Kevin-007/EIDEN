"""
Web automation capabilities - browse, search, fetch information.
"""
import logging
import re
from typing import Optional, Dict, Any
import webbrowser
from urllib.parse import quote_plus

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests/bs4 not available - web fetching limited")


class WebAutomation:
    """Web browsing and information fetching."""
    
    def __init__(self):
        self.logger = logging.getLogger('jarvis.web_automation')
        self.session = requests.Session() if REQUESTS_AVAILABLE else None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_web(self, query: str, engine: str = "google") -> str:
        """Open web search in browser."""
        try:
            engines = {
                "google": f"https://www.google.com/search?q={quote_plus(query)}",
                "bing": f"https://www.bing.com/search?q={quote_plus(query)}",
                "duckduckgo": f"https://duckduckgo.com/?q={quote_plus(query)}",
                "youtube": f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            }
            
            url = engines.get(engine.lower(), engines["google"])
            webbrowser.open(url)
            
            self.logger.info(f"Opened {engine} search for: {query}")
            return f"Searching {engine} for {query}"
            
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return f"Failed to search: {e}"
    
    def open_website(self, url: str) -> str:
        """Open a website in default browser."""
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            self.logger.info(f"Opened website: {url}")
            return f"Opening {url}"
            
        except Exception as e:
            self.logger.error(f"Failed to open website: {e}")
            return f"Failed to open website: {e}"
    
    def fetch_webpage_content(self, url: str) -> Optional[str]:
        """Fetch and extract text content from webpage."""
        if not REQUESTS_AVAILABLE:
            return "Web fetching requires 'requests' and 'beautifulsoup4' packages"
        
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit length
            if len(text) > 5000:
                text = text[:5000] + "..."
            
            self.logger.info(f"Fetched content from: {url}")
            return text
            
        except Exception as e:
            self.logger.error(f"Failed to fetch webpage: {e}")
            return None
    
    def search_and_fetch(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """Search and fetch top results (requires requests)."""
        if not REQUESTS_AVAILABLE:
            return {"error": "Requires 'requests' and 'beautifulsoup4' packages"}
        
        try:
            # Use DuckDuckGo HTML search (no API key needed)
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            response = self.session.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            for result in soup.find_all('a', class_='result__a', limit=num_results):
                title = result.get_text(strip=True)
                url = result.get('href', '')
                
                if url:
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': self.fetch_webpage_content(url)
                    })
            
            return {
                'query': query,
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Search and fetch error: {e}")
            return {"error": str(e)}
    
    def get_weather_web(self, location: str) -> Optional[str]:
        """Fetch weather from web (fallback if API unavailable)."""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            url = f"https://wttr.in/{quote_plus(location)}?format=3"
            response = self.session.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            
            return response.text.strip()
            
        except Exception as e:
            self.logger.error(f"Weather fetch error: {e}")
            return None
    
    def get_news_headlines(self, topic: str = "world") -> list:
        """Fetch news headlines (simple scraping)."""
        if not REQUESTS_AVAILABLE:
            return []
        
        try:
            # Use Google News
            url = f"https://news.google.com/search?q={quote_plus(topic)}"
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            headlines = []
            for article in soup.find_all('article', limit=5):
                title_elem = article.find('h3') or article.find('h4')
                if title_elem:
                    headlines.append(title_elem.get_text(strip=True))
            
            return headlines
            
        except Exception as e:
            self.logger.error(f"News fetch error: {e}")
            return []
    
    def download_file(self, url: str, save_path: str) -> bool:
        """Download file from URL."""
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"Downloaded file to: {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Download error: {e}")
            return False
    
    def extract_emails(self, text: str) -> list:
        """Extract email addresses from text."""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)
    
    def extract_urls(self, text: str) -> list:
        """Extract URLs from text."""
        pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return re.findall(pattern, text)
    
    def shorten_url(self, url: str) -> Optional[str]:
        """Shorten URL using TinyURL."""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            api_url = f"http://tinyurl.com/api-create.php?url={quote_plus(url)}"
            response = self.session.get(api_url, timeout=5)
            response.raise_for_status()
            
            return response.text.strip()
            
        except Exception as e:
            self.logger.error(f"URL shortening error: {e}")
            return None
