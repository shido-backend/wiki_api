from urllib.parse import quote
from typing import List, Dict, Optional

class SearchService:
    def __init__(self, api, cache):
        self.api = api
        self.cache = cache
    
    async def search_articles(self, query: str) -> List[Dict]:
        if not query:
            raise ValueError("Query parameter is required")
        
        cache_key = f"search_{query}"
        cached = self.cache.get("search", cache_key)
        if cached:
            return cached
        
        data = await self.api.search(query)
        results = self._format_search_results(data)
        
        self.cache.set("search", cache_key, results)
        return results
    
    def _format_search_results(self, data: Dict) -> List[Dict]:
        return [
            {
                "title": item["title"], 
                "snippet": item["snippet"]
            } 
            for item in data.get("query", {}).get("search", [])
        ]
    
    