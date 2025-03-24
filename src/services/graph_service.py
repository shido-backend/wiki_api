import asyncio
from typing import Dict, List, Set, Optional
import json

class GraphService:
    def __init__(self, api, cache):
        self.api = api
        self.cache = cache
        self.max_depth = 3  

    async def get_links_cached(self, title: str) -> List[str]:
        cached = self.cache.get("links", title)
        if cached:
            return cached
        
        data = await self.api.get_links(title)
        page = next(iter(data.get("query", {}).get("pages", {}).values()), {})
        links = [link["title"] for link in page.get("links", [])]
        self.cache.set("links", title, links)
        return links

    async def generate_graph(self, start_title: str, depth: int) -> Dict:
        depth = min(depth, self.max_depth)
        visited = set()
        queue = [(start_title, 0)]
        nodes = {start_title}
        links = []

        while queue:
            current_title, current_depth = queue.pop(0)
            
            if current_depth >= depth or current_title in visited:
                continue
                
            visited.add(current_title)
            
            try:
                current_links = await self.get_links_cached(current_title)
                
                for link in current_links:
                    nodes.add(link)
                    links.append({
                        "source": current_title,
                        "target": link,
                        "depth": current_depth + 1
                    })
                    
                    if current_depth + 1 < depth:
                        queue.append((link, current_depth + 1))
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing {current_title}: {str(e)}")
                continue

        return {
            "nodes": list(nodes),
            "links": links
        }

    async def stream_graph(self, ws, start_title: str, depth: int):
        depth = min(depth, self.max_depth)
        visited = set()
        queue = [(start_title, 0)]
        
        # Отправляем начальный узел
        await self._send_node(ws, start_title)
        
        while queue:
            current_title, current_depth = queue.pop(0)
            
            if current_depth >= depth or current_title in visited:
                continue
                
            visited.add(current_title)
            
            try:
                links = await self.get_links_cached(current_title)
                
                for link in links:
                    await self._send_node(ws, link)
                    await self._send_link(ws, current_title, link)
                    
                    if current_depth + 1 < depth:
                        queue.append((link, current_depth + 1))
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing {current_title}: {str(e)}")
                continue

    async def _send_node(self, ws, node_id: str):
        await ws.send(json.dumps({
            "type": "node",
            "data": {"id": node_id}
        }))

    async def _send_link(self, ws, source: str, target: str):
        await ws.send(json.dumps({
            "type": "link",
            "data": {"source": source, "target": target}
        }))