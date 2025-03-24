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