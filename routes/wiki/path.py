import json
from sanic_ext import openapi
from routes.base import BaseRoute
from services.path_service import PathService

class PathRoute(BaseRoute):
    def __init__(self, bp, api, cache):
        super().__init__(bp, api, cache)
        self.service = PathService(api, cache)
    
    def register_routes(self):
        @self.bp.websocket("/path")
        async def find_path(request, ws):
            try:
                message = await ws.recv()
                params = json.loads(message)
                
                from_title = params.get("from", "Python (programming language)")
                to_title = params.get("to", "Machine learning")
                max_depth = min(int(params.get("depth", 3)), 5)
                
                await self.service.stream_path_search(ws, from_title, to_title, max_depth)
                
            except json.JSONDecodeError:
                await ws.send(json.dumps({"error": "Invalid JSON"}))
            except Exception as e:
                await ws.send(json.dumps({"error": str(e)}))
            finally:
                await ws.close()