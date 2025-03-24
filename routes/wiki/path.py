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
        @openapi.summary("Find path between Wikipedia articles (WebSocket)")
        @openapi.description(
            "Establishes WebSocket connection to find and stream paths between two Wikipedia articles. "
            "Client should send JSON message with parameters, server will stream progress and results."
        )
        @openapi.tag("Path Finding")
        @openapi.parameter(
            name="from",
            schema=str,
            required=False,
            location="message", 
            description="Starting article title (default: 'Python (programming language)')",
            example="Python (programming language)"
        )
        @openapi.parameter(
            name="to",
            schema=str,
            required=False,
            location="message",
            description="Target article title (default: 'Machine learning')",
            example="Machine learning"
        )
        @openapi.parameter(
            name="depth",
            schema=int,
            required=False,
            location="message",
            description="Maximum search depth (1-5, default: 3)",
            example=3
        )
        @openapi.response(
            description="WebSocket connection established",
            content={
                "application/json": {
                    "examples": {
                        "InitialConnection": {
                            "value": {
                                "status": "connected",
                                "message": "Send JSON parameters to begin search"
                            }
                        }
                    }
                }
            }
        )
        @openapi.response(
            description="Path progress updates",
            content={
                "application/json": {
                    "examples": {
                        "ProgressUpdate": {
                            "value": {
                                "status": "searching",
                                "current_depth": 2,
                                "nodes_visited": 42
                            }
                        },
                        "PathFound": {
                            "value": {
                                "status": "found",
                                "path": [
                                    "Python (programming language)",
                                    "Artificial intelligence",
                                    "Machine learning"
                                ],
                                "steps": 2,
                                "duration_ms": 1245
                            }
                        },
                        "Error": {
                            "value": {
                                "status": "error",
                                "error": "Target article not found within max depth"
                            }
                        }
                    }
                }
            }
        )
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