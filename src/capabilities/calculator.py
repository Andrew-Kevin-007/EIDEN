"""Calculator and unit converter capabilities."""
import math
import re
from typing import Dict, Any, Optional


class Calculator:
    """Mathematical calculations and unit conversions."""
    
    def __init__(self):
        """Initialize calculator."""
        self.conversion_factors = {
            # Length
            'meters_to_feet': 3.28084,
            'feet_to_meters': 0.3048,
            'miles_to_kilometers': 1.60934,
            'kilometers_to_miles': 0.621371,
            'inches_to_centimeters': 2.54,
            'centimeters_to_inches': 0.393701,
            
            # Weight
            'pounds_to_kilograms': 0.453592,
            'kilograms_to_pounds': 2.20462,
            'ounces_to_grams': 28.3495,
            'grams_to_ounces': 0.035274,
            
            # Temperature conversions handled separately
            
            # Volume
            'gallons_to_liters': 3.78541,
            'liters_to_gallons': 0.264172,
            'cups_to_milliliters': 236.588,
            'milliliters_to_cups': 0.00422675,
        }
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression.
        
        Args:
            expression: Math expression to evaluate
            
        Returns:
            Result dictionary
        """
        try:
            # Clean the expression
            expression = expression.lower().strip()
            
            # Replace word operators
            expression = expression.replace('plus', '+')
            expression = expression.replace('minus', '-')
            expression = expression.replace('times', '*')
            expression = expression.replace('multiplied by', '*')
            expression = expression.replace('divided by', '/')
            expression = expression.replace('to the power of', '**')
            expression = expression.replace('squared', '**2')
            expression = expression.replace('cubed', '**3')
            
            # Remove common phrases
            expression = re.sub(r'what is |calculate |compute |equals? ', '', expression)
            
            # Evaluate safely
            # Only allow numbers, basic operators, and math functions
            allowed_names = {
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'pi': math.pi,
                'e': math.e,
            }
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            return {
                "success": True,
                "message": f"{expression} = {result}",
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Could not calculate: {str(e)}"
            }
    
    def convert_temperature(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """Convert between temperature units."""
        try:
            from_unit = from_unit.lower()
            to_unit = to_unit.lower()
            
            # Convert to Celsius first
            if from_unit in ['f', 'fahrenheit']:
                celsius = (value - 32) * 5/9
            elif from_unit in ['c', 'celsius']:
                celsius = value
            elif from_unit in ['k', 'kelvin']:
                celsius = value - 273.15
            else:
                return {"success": False, "message": "Unknown temperature unit"}
            
            # Convert from Celsius to target
            if to_unit in ['f', 'fahrenheit']:
                result = celsius * 9/5 + 32
                unit_name = "°F"
            elif to_unit in ['c', 'celsius']:
                result = celsius
                unit_name = "°C"
            elif to_unit in ['k', 'kelvin']:
                result = celsius + 273.15
                unit_name = "K"
            else:
                return {"success": False, "message": "Unknown temperature unit"}
            
            return {
                "success": True,
                "message": f"{value}° {from_unit} = {result:.2f}{unit_name}",
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Conversion error: {str(e)}"
            }
    
    def convert_units(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """
        Convert between various units.
        
        Args:
            value: Value to convert
            from_unit: Source unit
            to_unit: Target unit
            
        Returns:
            Result dictionary
        """
        try:
            # Handle temperature separately
            if any(u in from_unit.lower() for u in ['celsius', 'fahrenheit', 'kelvin']):
                return self.convert_temperature(value, from_unit, to_unit)
            
            # Construct conversion key
            conversion_key = f"{from_unit.lower()}_to_{to_unit.lower()}"
            
            if conversion_key in self.conversion_factors:
                result = value * self.conversion_factors[conversion_key]
                return {
                    "success": True,
                    "message": f"{value} {from_unit} = {result:.2f} {to_unit}",
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "message": f"Conversion from {from_unit} to {to_unit} not supported"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Conversion error: {str(e)}"
            }
