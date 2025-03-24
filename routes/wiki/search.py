from sanic import response
from sanic_ext import openapi
from routes.base import BaseRoute
from services.search_service import SearchService

class SearchRoute(BaseRoute):
    def __init__(self, bp, api, cache):
        super().__init__(bp, api, cache)
        self.service = SearchService(api, cache)
    
    def register_routes(self):
        @self.bp.route("/search")
        async def search(request):
            try:
                query = request.args.get("q", "")
                results = await self.service.search_articles(query)
                return response.json(results)
            except ValueError as e:
                return await self.handle_error(str(e), 400)
            except Exception as e:
                return await self.handle_error(str(e), 500)