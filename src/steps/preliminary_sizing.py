# src/steps/preliminary_sizing.py

from math import ceil
from typing import Dict, Any
from ..core.design_step import DesignStep
from ..core.exceptions import DesignError, VerificationError, InputError
from ..utils.validators import validate_numeric_positive
from ..llm.consultant import LLMConsultant

class PreliminarySizing(DesignStep):
    """Step 1: Preliminary Member Sizing for Simply Supported RC Beams"""
    
    def __init__(self):
        super().__init__()
        self.step_name = "preliminary_sizing"
        self.min_depth_factor = 1/16  # ACI 318-19 Table 9.3.1.1

    def design(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate preliminary dimensions based on span length
        
        Parameters:
        -----------
        parameters : dict
            Must contain:
                - span_length: float (inches)
        """
        try:
            self._validate_design_inputs(parameters)
            span_length = parameters["span_length"]

            results = {
                "inputs": {"span_length": span_length},
                "calculations": {},
                "explanations": [],
                "requirements_check": {},
                "final_dimensions": {}
            }

            # depth calculation
            min_depth = self._calculate_min_depth(span_length)
            results["calculations"]["depth"] = min_depth["calculations"]
            results["explanations"].extend(min_depth["explanations"])
            design_depth = min_depth["design_depth"]

            # Width calculation
            width_data = self._calculate_width(design_depth)
            results["calculations"]["width"] = width_data["calculations"]
            results["explanations"].extend(width_data["explanations"])

            # Final output
            results["final_dimensions"] = {
                "depth": design_depth,
                "width": width_data["design_width"],
                "units": "inches"
            }

            return results

        except Exception as e:
            raise DesignError(self.step_name, str(e))

    def verify(self, provided_design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate provided dimensions against ACI requirements
        
        Parameters:
        -----------
        provided_design : dict
            Must contain:
                - span_length: float (inches)
                - depth: float (inches)
                - width: float (inches)
        """
        try:
            self._validate_verification_inputs(provided_design)
            span = provided_design["span_length"]
            h = provided_design["depth"]
            b = provided_design["width"]

            results = {
                "provided": {"depth": h, "width": b, "units": "inches"},
                "checks": {},
                "explanations": []
            }

            # depth check
            min_h = span * self.min_depth_factor
            h_check = h >= min_h
            results["checks"]["depth"] = {
                "required": f"≥ {min_h:.1f} in. (L/16)",
                "status": "PASS" if h_check else "FAIL",
                "explanation": (
                    f"ACI 318-19 Table 9.3.1.1 minimum depth: {min_h:.1f} in. "
                    f"(L/16)\nProvided: {h} in. | Status: {'PASS' if h_check else 'FAIL'}"
                )
            }

            # Width check
            min_b = h / 2
            max_b = 2 * h / 3
            b_check = min_b <= b <= max_b
            results["checks"]["width"] = {
                "required": f"{min_b:.1f}-{max_b:.1f} in. (h/2 to 2h/3)",
                "status": "PASS" if b_check else "FAIL",
                "explanation": (
                    f"Recommended width range: {min_b:.1f} to {max_b:.1f} in.\n"
                    f"Provided: {b} in. | Status: {'PASS' if b_check else 'FAIL'}"
                )
            }

            # Overall status
            results["overall"] = {
                "passed": h_check and b_check,
                "message": "All requirements met" if (h_check and b_check) 
                          else "Fails 1+ requirements"
            }

            return results

        except Exception as e:
            raise VerificationError(self.step_name, str(e))
        
    def check_requirements(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder implementation for abstract method"""
        return {"passed": True, "message": "Requirements check not implemented"}
    
    def _calculate_min_depth(self, span: float) -> Dict[str, Any]:
        """Calculate and round minimum beam depth"""
        min_h = span * self.min_depth_factor
        rounded_h = self._round_to_even(min_h)
        
        return {
            "calculations": {
                "formula": "L/16",
                "calculated": min_h,
                "rounded": rounded_h,
                "units": "inches"
            },
            "explanations": [
                f"Minimum depth per ACI 318-19: {min_h:.2f} in. "
                f"=> Rounded to {rounded_h} in. for constructability"
            ],
            "design_depth": rounded_h
        }

    def _calculate_width(self, depth: float) -> Dict[str, Any]:
        """Calculate recommended beam width"""
        min_b = depth / 2
        max_b = 2 * depth / 3
        ideal_b = (min_b + max_b) / 2
        rounded_b = self._round_to_even(ideal_b)

        # Ensure within practical limits
        final_b = min(max(rounded_b, self._round_to_even(min_b)), 
                    self._round_to_even(max_b))

        return {
            "calculations": {
                "min": {"value": min_b, "units": "inches"},
                "max": {"value": max_b, "units": "inches"},
                "recommended": {"value": final_b, "units": "inches"}
            },
            "explanations": [
                f"Width range: {min_b:.1f}-{max_b:.1f} in. "
                f"(Practical: h/2 to 2h/3)\n"
                f"Selected width: {final_b} in. (rounded even number)"
            ],
            "design_width": final_b
        }

    @staticmethod
    def _round_to_even(value: float) -> int:
        """Round up to nearest even integer"""
        rounded = ceil(value)
        return rounded if rounded % 2 == 0 else rounded + 1

    def _validate_design_inputs(self, params: Dict):
        """Validate design mode inputs"""
        if "span_length" not in params:
            raise InputError("span_length", "Required for design mode")
        validate_numeric_positive(params["span_length"], "span_length")

    def _validate_verification_inputs(self, params: Dict):
        """Validate verification mode inputs"""
        required = ["span_length", "depth", "width"]
        for param in required:
            if param not in params:
                raise InputError(param, "Required for verification")
            validate_numeric_positive(params[param], param)

    def request_llm_feedback(self, design_results: Dict[str, Any], api_key:str) -> str:
        """Requests feedback from the LLM on the design results."""
        consultant = LLMConsultant(api_key)
        return consultant.get_preliminary_sizing_feedback(design_results)
            
if __name__=="__main__":
    designer = PreliminarySizing()
    result = designer.design({"span_length": 240})  # 20 ft span
    provided={'span_length':120,'depth':20,'width':10}
    result=designer.verify(provided)
    print(result)
    # Output: {"depth": 16, "width": 10, "units": "inches"}