from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .exceptions import DesignError, VerificationError,InputError

class DesignStep(ABC):
    """Base class for all RC beam design steps"""
    
    def __init__(self):
        self.step_name: str = "base_step"
        self.results: Dict[str, Any] = {
            "design_mode": {},
            "verify_mode": {}
        }
    
    @abstractmethod
    def design(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute design calculations"""
        pass
    
    @abstractmethod
    def verify(self, proposed_design: Dict[str, Any]) -> Dict[str, Any]:
        """Verify proposed design"""
        pass
    
    @abstractmethod
    def check_requirements(self, results: Dict[str, Any]) -> Dict[str, bool]:
        """Check if results meet code requirements"""
        pass
    
    def _validate_inputs(self, parameters: Dict[str, Any], required_params: list) -> None:
        """Validate input parameters"""
        for param in required_params:
            if param not in parameters:
                raise InputError(param, "Required parameter missing")