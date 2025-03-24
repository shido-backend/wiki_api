import json
from collections import deque
from typing import Dict, List, Set, Optional, Deque, Tuple

class PathService:
    def __init__(self, api, cache):
        self.api = api
        self.cache = cache
        self.max_depth = 5

    async def get_links_cached(self, title: str) -> List[str]:
        cached = self.cache.get("links", title)
        if cached:
            return cached
        
        data = await self.api.get_links(title)
        page = next(iter(data.get("query", {}).get("pages", {}).values()), {})
        links = [link["title"] for link in page.get("links", [])]
        self.cache.set("links", title, links)
        return links

    async def find_path(self, from_title: str, to_title: str, max_depth: int) -> Dict:
        max_depth = min(max_depth, self.max_depth)
        queue = deque([(from_title, [from_title])])
        visited = set()
        
        while queue:
            current_title, path = queue.popleft()
            
            if current_title == to_title:
                return {
                    "found": True,
                    "path": path,
                    "message": "Path found"
                }
            
            if len(path) >= max_depth:
                continue
            
            try:
                links = await self.get_links_cached(current_title)
                for link in links:
                    if link not in visited:
                        visited.add(link)
                        queue.append((link, path + [link]))
            except Exception as e:
                print(f"Error processing {current_title}: {e}")
                continue
        
        return {
            "found": False,
            "path": [],
            "message": f"Path not found within {max_depth} steps"
        }

    async def stream_path_search(self, ws, from_title: str, to_title: str, max_depth: int):
        max_depth = min(max_depth, self.max_depth)
        queue = deque([(from_title, [from_title])])
        visited = set()
        
        while queue:
            current_title, path = queue.popleft()

            await self._send_progress(ws, current_title, path)
            
            if current_title == to_title:
                await self._send_result(ws, path, True)
                return
            
            if len(path) >= max_depth:
                continue
            
            try:
                links = await self.get_links_cached(current_title)
                for link in links:
                    if link not in visited:
                        visited.add(link)
                        queue.append((link, path + [link]))
            except Exception as e:
                print(f"Error processing {current_title}: {e}")
                continue
        
        await self._send_result(ws, [], False, f"Path not found within {max_depth} steps")

    async def _send_progress(self, ws, current_title: str, path: List[str]):
        await ws.send(json.dumps({
            "type": "progress",
            "current": current_title,
            "path": path
        }))

    async def _send_result(self, ws, path: List[str], found: bool, message: str = ""):
        await ws.send(json.dumps({
            "type": "result",
            "path": path,
            "found": found,
            "message": message
        }))