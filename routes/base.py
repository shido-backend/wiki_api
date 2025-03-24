from sanic import response
from sanic.response import json as json_response

class BaseRoute:
    def __init__(self, bp, api, cache): 
        self.bp = bp 
        self.api = api
        self.cache = cache
    
    def register_routes(self):
        raise NotImplementedError("Subclasses must implement register_routes method")
    
    async def handle_error(self, message, status=400):
        return json_response({"error": message}, status=status)