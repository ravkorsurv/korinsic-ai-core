"""Mock Risk Calculator for testing"""

class RiskCalculator:
    """Mock Risk Calculator class"""
    
    def __init__(self):
        self.initialized = True
    
    def calculate_risk(self, data):
        """Mock risk calculation method"""
        return {"risk_score": 0.5, "mock": True}
