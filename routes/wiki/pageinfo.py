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
        @openapi.parameter(
            name="title",
            schema=str,
            required=True,
            location="query",
            description="Название страницы Wikipedia для получения информации",
            example="Python (programming language)"
        )
        @openapi.response(
            status=200,
            description="Успешный запрос информации о странице",
            content={
                "application/json": {
                    "example": {
                        "title": "Python (programming language)",
                        "pageid": 23862,
                        "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
                        "extract": "Python is a high-level, general-purpose programming language...",
                        "categories": ["Programming languages", "Python (programming language)"],
                        "last_edited": "2023-05-15T08:42:31Z",
                        "pageviews": 1500000
                    }
                }
            }
        )
        @openapi.response(
            status=400,
            description="Неверный запрос - отсутствует параметр title",
            content={
                "application/json": {
                    "example": {
                        "error": "Параметр 'title' обязателен"
                    }
                }
            }
        )
        @openapi.response(
            status=404,
            description="Страница не найдена",
            content={
                "application/json": {
                    "example": {
                        "error": "Страница не найдена"
                    }
                }
            }
        )
        @openapi.response(
            status=500,
            description="Внутренняя ошибка сервера",
            content={
                "application/json": {
                    "example": {
                        "error": "Произошла внутренняя ошибка сервера"
                    }
                }
            }
        )
        @openapi.summary("Получить информацию о странице Wikipedia")
        @openapi.description(
            "Возвращает подробную информацию о запрошенной странице Wikipedia, "
            "включая краткое описание, категории, дату последнего редактирования и другую метаинформацию."
        )
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