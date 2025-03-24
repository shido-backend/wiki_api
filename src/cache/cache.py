from collections import defaultdict

class CacheManager:
    def __init__(self):
        self.cache = defaultdict(dict)
    
    def get(self, namespace, key):
        return self.cache[namespace].get(key)
    
    def set(self, namespace, key, value):
        self.cache[namespace][key] = value
    
    def clear(self, namespace=None):
        if namespace:
            self.cache[namespace].clear()
        else:
            self.cache.clear()

cache = CacheManager()