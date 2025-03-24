from sanic import response
from sanic_ext import openapi
from routes.base import BaseRoute
from services.timeline_service import TimelineService

class TimelineRoute(BaseRoute):
    def __init__(self, bp, api, cache):
        super().__init__(bp, api, cache)
        self.service = TimelineService(api)
    
    def register_routes(self):
        @self.bp.route("/timeline")
        @openapi.parameter(
            name="title",
            schema=str,
            required=True,
            location="query",
            description="Title of the Wikipedia page to get timeline for"
        )
        @openapi.response(
            status=200,
            description="Successful timeline data",
            content={
                "application/json": {
                    "example": {
                        "title": "Python (programming language)",
                        "timeline": [
                            {
                                "year": 1991,
                                "event": "First release of Python"
                            },
                            {
                                "year": 2000,
                                "event": "Python 2.0 released"
                            }
                        ]
                    }
                }
            }
        )
        @openapi.response(
            status=400,
            description="Bad request - invalid parameters",
            content={
                "application/json": {
                    "example": {
                        "error": "Title parameter is required"
                    }
                }
            }
        )
        @openapi.response(
            status=404,
            description="Page not found",
            content={
                "application/json": {
                    "example": {
                        "error": "Page not found"
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
        @openapi.summary("Get historical timeline for a Wikipedia page")
        @openapi.description("Returns chronological events and milestones for a given Wikipedia article")
        async def timeline(request):
            try:
                title = request.args.get("title", "")
                timeline_data = await self.service.get_page_timeline(title)
                return response.json(timeline_data)
            except ValueError as e:
                status = 404 if str(e) == "Page not found" else 400
                return await self.handle_error(str(e), status)
            except Exception as e:
                return await self.handle_error(str(e), 500)