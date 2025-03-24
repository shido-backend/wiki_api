from sanic import Blueprint
from .search import SearchRoute
from .pageinfo import PageInfoRoute
from .timeline import TimelineRoute
from .path import PathRoute
from .graph import GraphRoute

def setup_wiki_routes(app, api, cache):
    # Создаем блюпринт с правильным url_prefix
    wiki_bp = Blueprint("wiki", url_prefix="/wiki")
    
    # Инициализируем роутеры
    SearchRoute(wiki_bp, api, cache).register_routes()
    PageInfoRoute(wiki_bp, api, cache).register_routes()
    TimelineRoute(wiki_bp, api, cache).register_routes()
    PathRoute(wiki_bp, api, cache).register_routes()
    GraphRoute(wiki_bp, api, cache).register_routes()
    
    # Регистрируем блюпринт
    app.blueprint(wiki_bp)