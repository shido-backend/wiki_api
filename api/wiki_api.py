import aiohttp
from urllib.parse import quote
from config import Config

class WikipediaAPI:
    def __init__(self):
        self.base_url = Config.WIKI_API
    
    async def fetch(self, params):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as resp:
                return await resp.json()
    
    async def search(self, query, limit=10):
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": limit
        }
        return await self.fetch(params)
    
    async def get_page_info(self, title, links_limit=50):
        params = {
            "action": "query",
            "prop": "info|revisions|links",
            "titles": title,
            "format": "json",
            "inprop": "url",
            "rvprop": "timestamp",
            "pllimit": links_limit
        }
        return await self.fetch(params)
    
    async def get_timeline(self, title, limit=500):
        params = {
            "action": "query",
            "prop": "revisions",
            "titles": title,
            "format": "json",
            "rvlimit": limit,
            "rvdir": "newer"
        }
        return await self.fetch(params)
    
    async def get_links(self, title, limit=50):
        params = {
            "action": "query",
            "prop": "links",
            "titles": title,
            "format": "json",
            "pllimit": limit
        }
        return await self.fetch(params)

wiki_api = WikipediaAPI()