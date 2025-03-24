from urllib.parse import quote
from typing import Dict, Optional, List

class PageService:
    def __init__(self, api, cache):
        self.api = api
        self.cache = cache
    
    async def get_page_info(self, title: str) -> Dict:
        if not title:
            raise ValueError("Не указан заголовок")
        
        cache_key = f"page_{title}"
        cached = self.cache.get("pages", cache_key)
        if cached:
            return cached
        
        data = await self.api.get_page_info(title)
        page = next(iter(data.get("query", {}).get("pages", {}).values()), None)
        
        if not page or "missing" in page:
            raise ValueError("Страница не найдена")
        
        result = self._format_page_info(page, title)
        self.cache.set("pages", cache_key, result)
        
        return result
    
    def _format_page_info(self, page: Dict, original_title: str) -> Dict:
        revisions = page.get("revisions", [{}])
        
        return {
            "title": page.get("title", original_title),
            "url": page.get("fullurl", self._generate_page_url(original_title)),
            "last_modified": revisions[0].get("timestamp") if revisions else None,
            "links": [link["title"] for link in page.get("links", [])][:50]
        }
    
    def _generate_page_url(self, title: str) -> str:
        return f"https://en.wikipedia.org/wiki/{quote(title)}"