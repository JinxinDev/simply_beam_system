from typing import Dict, Any, List
from ..core.exceptions import InputError

def validate_numeric_positive(value: float, param_name: str) -> None:
    """Validate numeric parameter is positive"""
    if not isinstance(value, (int, float)):
        raise InputError(param_name, "Must be a number")
    if value <= 0:
        raise InputError(param_name, "Must be positive")

def validate_design_parameters(parameters: Dict[str, Any], 
                             required_params: List[str]) -> None:
    """Validate design input parameters"""
    # Check required parameters are present
    for param in required_params:
        if param not in parameters:
            raise InputError(param, "Required parameter missing")
            
    # Validate span length
    if "span_length" in parameters:
        validate_numeric_positive(parameters["span_length"], "span_length")
        
    # Validate support condition
    if "support_condition" in parameters:
        valid_conditions = ["simply_supported"]
        if parameters["support_condition"] not in valid_conditions:
            raise InputError("support_condition", 
                           f"Must be one of {valid_conditions}")