import json
from sanic_ext import openapi
from routes.base import BaseRoute
from services.graph_service import GraphService

class GraphRoute(BaseRoute):
    def __init__(self, bp, api, cache):
        super().__init__(bp, api, cache)
        self.service = GraphService(api, cache)
    
    def register_routes(self):
        @self.bp.websocket("/graph")
        async def knowledge_graph(request, ws):
            try:
                message = await ws.recv()
                params = json.loads(message)
                
                start_title = params.get("title", "Python (programming language)")
                depth = min(int(params.get("depth", 2)), 3)
                
                await self.service.stream_graph(ws, start_title, depth)
                
            except json.JSONDecodeError:
                await ws.send(json.dumps({"error": "Invalid JSON"}))
            except Exception as e:
                print(f"WebSocket error: {str(e)}")
                await ws.send(json.dumps({"error": str(e)}))
            finally:
                await ws.close()