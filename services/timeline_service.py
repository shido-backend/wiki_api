from typing import Dict, List, Optional

class TimelineService:
    def __init__(self, api):
        self.api = api
    
    async def get_page_timeline(self, title: str) -> Dict:
        if not title:
            raise ValueError("Missing title parameter")
        
        data = await self.api.get_timeline(title)
        page = next(iter(data.get("query", {}).get("pages", {}).values()), None)
        
        if not page or "missing" in page:
            raise ValueError("Page not found")
        
        return {
            "title": page["title"],
            "timeline": self._format_timeline_data(page.get("revisions", []))
        }
    
    def _format_timeline_data(self, revisions: List[Dict]) -> List[Dict]:
        return [
            {
                "timestamp": rev["timestamp"],
                "user": rev.get("user", "Anonymous"),
                "event": "Edit"
            }
            for rev in revisions
        ]