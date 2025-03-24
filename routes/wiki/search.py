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
        @openapi.parameter(
            name="q",
            schema=str,
            required=True,
            location="query",
            description="Search query string"
        )
        @openapi.parameter(
            name="limit",
            schema=int,
            required=False,
            location="query",
            description="Maximum number of results to return (default: 10)"
        )
        @openapi.response(
            status=200,
            description="Successful search results",
            content={
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "title": "Python (programming language)",
                                "pageid": 23862,
                                "snippet": "Python is a high-level, general-purpose programming language..."
                            }
                        ],
                        "count": 1
                    }
                }
            }
        )
        @openapi.response(
            status=400,
            description="Bad request - invalid query parameters",
            content={
                "application/json": {
                    "example": {
                        "error": "Query parameter 'q' is required"
                    }
                }
            }
        )
        @openapi.response(
            status=500,
            description="Internal server error",
            content={
                "application/json": {
                    "example": {
                        "error": "Internal server error occurred"
                    }
                }
            }
        )
        @openapi.summary("Search Wikipedia articles")
        @openapi.description("Performs a search query against Wikipedia and returns matching articles")
        async def search(request):
            try:
                query = request.args.get("q", "")
                results = await self.service.search_articles(query)
                return response.json(results)
            except ValueError as e:
                return await self.handle_error(str(e), 400)
            except Exception as e:
                return await self.handle_error(str(e), 500)