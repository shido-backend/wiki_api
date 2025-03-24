from sanic import response
from sanic_ext import openapi
from routes.base import BaseRoute
from services.pageinfo_service import PageService

class PageInfoRoute(BaseRoute):
    def __init__(self, bp, api, cache):
        super().__init__(bp, api, cache)
        self.service = PageService(api, cache)
    
    def register_routes(self):
        @self.bp.route("/pageinfo")
        async def page_info(request):
            try:
                title = request.args.get("title", "")
                page_data = await self.service.get_page_info(title)
                return response.json(page_data)
            except ValueError as e:
                status = 404 if str(e) == "Страница не найдена" else 400
                return await self.handle_error(str(e), status)
            except Exception as e:
                return await self.handle_error(str(e), 500)