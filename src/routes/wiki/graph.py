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
        @openapi.summary("Generate knowledge graph from Wikipedia article (WebSocket)")
        @openapi.description(
            "Establishes WebSocket connection to generate and stream a knowledge graph "
            "starting from the specified Wikipedia article. Client should send JSON message "
            "with parameters, server will stream graph nodes and relationships."
        )
        @openapi.tag("Knowledge Graph")
        @openapi.parameter(
            name="title",
            schema=str,
            required=False,
            location="message",
            description="Starting article title (default: 'Python (programming language)')",
            example="Python (programming language)"
        )
        @openapi.parameter(
            name="depth",
            schema=int,
            required=False,
            location="message",
            description="Graph exploration depth (1-3, default: 2)",
            example=2
        )
        @openapi.response(
            description="WebSocket connection established",
            content={
                "application/json": {
                    "example": {
                        "status": "connected",
                        "message": "Send JSON parameters to begin graph generation"
                    }
                }
            }
        )
        @openapi.response(
            description="Graph data stream",
            content={
                "application/json": {
                    "examples": {
                        "NodeAdded": {
                            "value": {
                                "type": "node",
                                "id": "Python_(programming_language)",
                                "label": "Python (programming language)",
                                "properties": {
                                    "pageviews": 1500000,
                                    "category": "Programming languages"
                                }
                            }
                        },
                        "RelationshipAdded": {
                            "value": {
                                "type": "relationship",
                                "source": "Python_(programming_language)",
                                "target": "Guido_van_Rossum",
                                "relationship": "CREATED_BY"
                            }
                        },
                        "ProgressUpdate": {
                            "value": {
                                "type": "progress",
                                "current_depth": 2,
                                "nodes_processed": 42,
                                "status": "exploring"
                            }
                        },
                        "Completion": {
                            "value": {
                                "type": "status",
                                "status": "complete",
                                "total_nodes": 58,
                                "total_relationships": 72,
                                "duration_seconds": 3.14
                            }
                        },
                        "Error": {
                            "value": {
                                "type": "error",
                                "error": "Invalid depth parameter",
                                "details": "Depth must be between 1 and 3"
                            }
                        }
                    }
                }
            }
        )
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