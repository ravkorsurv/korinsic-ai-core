"""Mock Data Processor for testing"""

class DataProcessor:
    """Mock Data Processor class"""
    
    def __init__(self):
        self.initialized = True
    
    def process(self, data):
        """Mock process method"""
        return {"processed": True, "mock": True}
