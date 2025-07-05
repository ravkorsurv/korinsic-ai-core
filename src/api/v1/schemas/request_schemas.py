"""
Request schemas for API v1 validation.

This module contains schema classes for validating incoming API requests.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class BaseRequestSchema:
    """Base class for request schemas."""
    
    def validate(self, data: Dict[str, Any]) -> 'ValidationResult':
        """
        Validate request data.
        
        Args:
            data: Request data to validate
            
        Returns:
            ValidationResult indicating success or failure
        """
        from ..middleware.validation import ValidationResult
        
        result = ValidationResult()
        
        try:
            # Perform basic validation
            self._validate_basic_structure(data, result)
            
            # Perform specific validation if basic validation passes
            if result.is_valid:
                self._validate_specific(data, result)
                
        except Exception as e:
            result.add_error(f"Validation error: {str(e)}")
        
        return result
    
    def _validate_basic_structure(self, data: Dict[str, Any], result: 'ValidationResult'):
        """Validate basic data structure."""
        if not isinstance(data, dict):
            result.add_error("Request data must be a dictionary")
    
    def _validate_specific(self, data: Dict[str, Any], result: 'ValidationResult'):
        """Validate specific schema requirements. Override in subclasses."""
        pass


class AnalysisRequestSchema(BaseRequestSchema):
    """Schema for analysis request validation."""
    
    def _validate_specific(self, data: Dict[str, Any], result: 'ValidationResult'):
        """Validate analysis request specific requirements."""
        # Check required fields
        required_fields = ['trades', 'trader_info']
        for field in required_fields:
            if field not in data:
                result.add_error(f"Missing required field: {field}")
        
        if not result.is_valid:
            return
        
        # Validate trades
        self._validate_trades(data.get('trades', []), result)
        
        # Validate trader info
        self._validate_trader_info(data.get('trader_info', {}), result)
        
        # Validate optional fields
        if 'orders' in data:
            self._validate_orders(data['orders'], result)
        
        if 'material_events' in data:
            self._validate_material_events(data['material_events'], result)
        
        if 'market_data' in data:
            self._validate_market_data(data['market_data'], result)
    
    def _validate_trades(self, trades: List[Dict[str, Any]], result: 'ValidationResult'):
        """Validate trades data."""
        if not isinstance(trades, list):
            result.add_error("Trades must be a list")
            return
        
        if len(trades) == 0:
            result.add_error("Trades list cannot be empty")
            return
        
        required_trade_fields = ['id', 'timestamp', 'instrument', 'volume', 'price', 'side', 'trader_id']
        
        for i, trade in enumerate(trades):
            if not isinstance(trade, dict):
                result.add_error(f"Trade {i} must be a dictionary")
                continue
            
            for field in required_trade_fields:
                if field not in trade:
                    result.add_error(f"Trade {i} missing required field: {field}")
            
            # Validate trade field types
            if 'volume' in trade and not isinstance(trade['volume'], (int, float)):
                result.add_error(f"Trade {i} volume must be numeric")
            
            if 'price' in trade and not isinstance(trade['price'], (int, float)):
                result.add_error(f"Trade {i} price must be numeric")
            
            if 'side' in trade and trade['side'] not in ['buy', 'sell']:
                result.add_error(f"Trade {i} side must be 'buy' or 'sell'")
    
    def _validate_trader_info(self, trader_info: Dict[str, Any], result: 'ValidationResult'):
        """Validate trader info data."""
        if not isinstance(trader_info, dict):
            result.add_error("Trader info must be a dictionary")
            return
        
        required_fields = ['id', 'role']
        for field in required_fields:
            if field not in trader_info:
                result.add_error(f"Trader info missing required field: {field}")
        
        # Validate access level if provided
        if 'access_level' in trader_info:
            valid_levels = ['low', 'medium', 'high']
            if trader_info['access_level'] not in valid_levels:
                result.add_error(f"Invalid access level. Must be one of: {valid_levels}")
    
    def _validate_orders(self, orders: List[Dict[str, Any]], result: 'ValidationResult'):
        """Validate orders data."""
        if not isinstance(orders, list):
            result.add_error("Orders must be a list")
            return
        
        required_order_fields = ['id', 'timestamp', 'instrument', 'volume', 'price', 'side', 'status', 'trader_id']
        
        for i, order in enumerate(orders):
            if not isinstance(order, dict):
                result.add_error(f"Order {i} must be a dictionary")
                continue
            
            for field in required_order_fields:
                if field not in order:
                    result.add_error(f"Order {i} missing required field: {field}")
            
            # Validate order status
            if 'status' in order:
                valid_statuses = ['filled', 'cancelled', 'partial', 'pending']
                if order['status'] not in valid_statuses:
                    result.add_error(f"Order {i} invalid status. Must be one of: {valid_statuses}")
    
    def _validate_material_events(self, events: List[Dict[str, Any]], result: 'ValidationResult'):
        """Validate material events data."""
        if not isinstance(events, list):
            result.add_error("Material events must be a list")
            return
        
        for i, event in enumerate(events):
            if not isinstance(event, dict):
                result.add_error(f"Material event {i} must be a dictionary")
                continue
            
            required_fields = ['id', 'timestamp', 'type', 'instruments_affected']
            for field in required_fields:
                if field not in event:
                    result.add_error(f"Material event {i} missing required field: {field}")
    
    def _validate_market_data(self, market_data: Dict[str, Any], result: 'ValidationResult'):
        """Validate market data."""
        if not isinstance(market_data, dict):
            result.add_error("Market data must be a dictionary")
            return
        
        # Validate numeric fields
        numeric_fields = ['volatility', 'volume', 'price_movement']
        for field in numeric_fields:
            if field in market_data and not isinstance(market_data[field], (int, float)):
                result.add_error(f"Market data {field} must be numeric")


class SimulationRequestSchema(BaseRequestSchema):
    """Schema for simulation request validation."""
    
    def _validate_specific(self, data: Dict[str, Any], result: 'ValidationResult'):
        """Validate simulation request specific requirements."""
        # Check required fields
        if 'scenario_type' not in data:
            result.add_error("Missing required field: scenario_type")
        
        # Validate scenario type
        if 'scenario_type' in data:
            valid_types = ['insider_dealing', 'spoofing']
            if data['scenario_type'] not in valid_types:
                result.add_error(f"Invalid scenario type. Must be one of: {valid_types}")
        
        # Validate parameters if provided
        if 'parameters' in data:
            if not isinstance(data['parameters'], dict):
                result.add_error("Parameters must be a dictionary")


class BatchAnalysisRequestSchema(BaseRequestSchema):
    """Schema for batch analysis request validation."""
    
    def _validate_specific(self, data: Dict[str, Any], result: 'ValidationResult'):
        """Validate batch analysis request specific requirements."""
        if 'batch_data' not in data:
            result.add_error("Missing required field: batch_data")
            return
        
        batch_data = data['batch_data']
        if not isinstance(batch_data, list):
            result.add_error("Batch data must be a list")
            return
        
        if len(batch_data) == 0:
            result.add_error("Batch data cannot be empty")
            return
        
        # Validate each item in batch
        analysis_schema = AnalysisRequestSchema()
        for i, item in enumerate(batch_data):
            item_result = analysis_schema.validate(item)
            if not item_result.is_valid:
                for error in item_result.errors:
                    result.add_error(f"Batch item {i}: {error}")


class ExportRequestSchema(BaseRequestSchema):
    """Schema for export request validation."""
    
    def _validate_specific(self, data: Dict[str, Any], result: 'ValidationResult'):
        """Validate export request specific requirements."""
        # This would be similar to analysis request but might have different requirements
        # For now, use the same validation as analysis request
        analysis_schema = AnalysisRequestSchema()
        analysis_result = analysis_schema.validate(data)
        
        if not analysis_result.is_valid:
            for error in analysis_result.errors:
                result.add_error(error)