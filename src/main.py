from sanic import Sanic
from sanic_ext import Extend
from config import Config
from cache.cache import cache
from api.wiki_api import wiki_api
from routes.wiki import setup_wiki_routes

def create_app():
    app = Sanic("KnowledgeMap")
    
    # Настройка расширений (должно быть ПЕРВЫМ)
    Extend(app, extensions=[], config={
        "OAS_UI_DEFAULT": "swagger",
        "OAS_URL_PREFIX": "/docs",
        "API_TITLE": "KnowledgeMap API",
        "API_DESCRIPTION": "Wikipedia Knowledge Graph API",
        "API_VERSION": "1.0.0",
        "API_CONTACT_EMAIL": "your@email.com"
    })
    
    # Затем регистрируем роуты
    setup_wiki_routes(app, wiki_api, cache)
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(
        host=Config.DEFAULT_HOST,
        port=Config.DEFAULT_PORT,
        debug=Config.DEBUG,
        auto_reload=True
    )