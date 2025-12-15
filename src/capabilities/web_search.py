"""Web search and browsing capabilities."""
import webbrowser
import requests
from typing import Dict, Any, Optional
from urllib.parse import quote_plus


class WebSearcher:
    """Handle web searches and browser operations."""
    
    def __init__(self):
        """Initialize web searcher."""
        self.search_engines = {
            "google": "https://www.google.com/search?q={}",
            "bing": "https://www.bing.com/search?q={}",
            "duckduckgo": "https://duckduckgo.com/?q={}",
            "youtube": "https://www.youtube.com/results?search_query={}",
        }
        self.default_engine = "google"
    
    def search(self, query: str, engine: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform a web search.
        
        Args:
            query: Search query
            engine: Search engine to use (default: google)
            
        Returns:
            Result dictionary
        """
        try:
            engine = engine or self.default_engine
            if engine not in self.search_engines:
                engine = self.default_engine
            
            search_url = self.search_engines[engine].format(quote_plus(query))
            webbrowser.open(search_url)
            
            return {
                "success": True,
                "message": f"Searching {engine} for: {query}",
                "url": search_url
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Search failed: {str(e)}"
            }
    
    def open_website(self, url: str) -> Dict[str, Any]:
        """
        Open a website in the default browser.
        
        Args:
            url: Website URL
            
        Returns:
            Result dictionary
        """
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            return {
                "success": True,
                "message": f"Opening {url}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to open website: {str(e)}"
            }
    
    def search_youtube(self, query: str) -> Dict[str, Any]:
        """Search YouTube for videos."""
        return self.search(query, engine="youtube")
    
    def get_quick_answer(self, query: str) -> Optional[str]:
        """
        Try to get a quick answer from a search engine.
        Uses DuckDuckGo Instant Answer API.
        
        Args:
            query: Search query
            
        Returns:
            Quick answer text or None
        """
        try:
            # DuckDuckGo Instant Answer API
            api_url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json"
            response = requests.get(api_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Try to extract answer
                answer = (
                    data.get('AbstractText') or
                    data.get('Answer') or
                    data.get('Definition') or
                    None
                )
                
                return answer
                
        except Exception as e:
            print(f"Quick answer error: {e}")
            return None
