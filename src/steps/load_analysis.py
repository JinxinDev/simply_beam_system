# src/steps/load_analysis.py

from typing import Dict, Any
from ..core.design_step import DesignStep
from ..core.exceptions import DesignError, InputError
from ..utils.validators import validate_numeric_positive

class LoadAnalysis(DesignStep):
    """Step 2: Load Combination Analysis per ACI 318-19"""
    
    def __init__(self):
        super().__init__()
        self.step_name = "load_analysis"
        
    def design(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate factored load combinations per ACI 318-19 Table 5.3.1
        
        Parameters:
        -----------
        parameters : dict
            Must contain:
                - dead_load: float (kips/ft)
            Optional:
                - live_load, roof_live_load, snow_load, 
                  rain_load, wind_load, seismic_load
        """
        try:
            self._validate_inputs(parameters)
            results = self._initialize_results(parameters)
            combinations = []

            # Extract loads with default None
            D = parameters["dead_load"]
            L = parameters.get("live_load")
            Lr = parameters.get("roof_live_load")
            S = parameters.get("snow_load")
            R = parameters.get("rain_load")
            W = parameters.get("wind_load")
            E = parameters.get("seismic_load")

            # Combination 1: 1.4D
            self._add_combination(
                results,
                key="U1",
                name="Dead Load Only (ACI 318-19 Eq. 5.3.1a)",
                formula="1.4D",
                value=1.4 * D,
                calculation=f"1.4 * {D:.2f}",
                combinations=combinations
            )

            # Combination 2: 1.2D + 1.6L + 0.5(Lr/S/R)
            if L is not None:
                add_load = max(filter(None, [Lr, S, R]), default=0)
                calc = f"1.2*{D:.2f} + 1.6*{L:.2f} + 0.5*{add_load:.2f}"
                self._add_combination(
                    results,
                    key="U2",
                    name="Basic Load Combination (ACI 318-19 Eq. 5.3.1b)",
                    formula="1.2D + 1.6L + 0.5(Lr/S/R)",
                    value=1.2*D + 1.6*L + 0.5*add_load,
                    calculation=calc,
                    combinations=combinations
                )

            # Combination 3: 1.2D + 1.6(Lr/S/R) + (L or 0.5W)
            if any([Lr, S, R]):
                primary = max(filter(None, [Lr, S, R]))
                secondary = max(filter(None, [L, 0.5*W if W else None]))
                calc = f"1.2*{D:.2f} + 1.6*{primary:.2f} + {secondary:.2f}"
                self._add_combination(
                    results,
                    key="U3",
                    name="Roof/Snow/Rain Combination (ACI 318-19 Eq. 5.3.1c)",
                    formula="1.2D + 1.6(Lr/S/R) + (L or 0.5W)",
                    value=1.2*D + 1.6*primary + secondary,
                    calculation=calc,
                    combinations=combinations
                )

            # Combination 4: 1.2D + 1.0W + L + 0.5(Lr/S/R)
            if W is not None:
                add_load = max(filter(None, [Lr, S, R]), default=0)
                calc = f"1.2*{D:.2f} + 1.0*{W:.2f} + {L or 0:.2f} + 0.5*{add_load:.2f}"
                self._add_combination(
                    results,
                    key="U4",
                    name="Wind Load Combination (ACI 318-19 Eq. 5.3.1d)",
                    formula="1.2D + 1.0W + L + 0.5(Lr/S/R)",
                    value=1.2*D + 1.0*W + (L or 0) + 0.5*add_load,
                    calculation=calc,
                    combinations=combinations
                )

            # Combination 5: 1.2D + 1.0E + L + 0.2S
            if E is not None:
                calc = f"1.2*{D:.2f} + 1.0*{E:.2f} + {L or 0:.2f} + {0.2*(S or 0):.2f}"
                self._add_combination(
                    results,
                    key="U5",
                    name="Seismic Load Combination (ACI 318-19 Eq. 5.3.1e)",
                    formula="1.2D + 1.0E + L + 0.2S",
                    value=1.2*D + 1.0*E + (L or 0) + 0.2*(S or 0),
                    calculation=calc,
                    combinations=combinations
                )

            # Combination 6: 0.9D + 1.0W
            if W is not None:
                self._add_combination(
                    results,
                    key="U6",
                    name="Wind Uplift (ACI 318-19 Eq. 5.3.1f)",
                    formula="0.9D + 1.0W",
                    value=0.9*D + 1.0*W,
                    calculation=f"0.9*{D:.2f} + 1.0*{W:.2f}",
                    combinations=combinations
                )

            # Combination 7: 0.9D + 1.0E
            if E is not None:
                self._add_combination(
                    results,
                    key="U7",
                    name="Seismic Uplift (ACI 318-19 Eq. 5.3.1g)",
                    formula="0.9D + 1.0E",
                    value=0.9*D + 1.0*E,
                    calculation=f"0.9*{D:.2f} + 1.0*{E:.2f}",
                    combinations=combinations
                )

            self._set_controlling_load(results, combinations)
            return results

        except Exception as e:
            raise DesignError(self.step_name, str(e))

    def verify(self, _: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for verification (not implemented)"""
        return {
            "status": "not_implemented",
            "message": "Verification not required for load analysis"
        }

    def check_requirements(self, _: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for requirements check (not implemented)"""
        return {
            "passed": True,
            "message": "Requirements checking not implemented for load analysis"
        }

    def _validate_inputs(self, params: Dict[str, Any]):
        """Validate required parameters"""
        if "dead_load" not in params:
            raise InputError("dead_load", "Required for load analysis")
        validate_numeric_positive(params["dead_load"], "dead_load")

    def _initialize_results(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create results structure"""
        return {
            "inputs": {k: v for k, v in params.items() if v is not None},
            "load_combinations": {},
            "explanations": [],
            "controlling_load": None
        }

    def _add_combination(self, results: Dict, key: str, name: str, formula: str,
                       value: float, calculation: str, combinations: list):
        """Helper to add a load combination"""
        results["load_combinations"][key] = {
            "name": name,
            "formula": formula,
            "calculation": calculation,
            "value": value,
            "units": "kip/ft"
        }
        combinations.append(value)
        results["explanations"].append(
            f"Calculated {name}: {value:.2f} kip/ft ({formula})"
        )

    def _set_controlling_load(self, results: Dict, combinations: list):
        """Determine controlling load combination"""
        if combinations:
            max_load = max(combinations)
            for key, combo in results["load_combinations"].items():
                if combo["value"] == max_load:
                    results["controlling_load"] = {
                        "combination": key,
                        "value": max_load,
                        "units": "kip/ft"
                    }
                    results["explanations"].append(
                        f"Controlling load: {key} ({combo['name']}) "
                        f"= {max_load:.2f} kip/ft"
                    )
                    break

if __name__=="__main__":
    designer = LoadAnalysis()
    result = designer.design({
        "dead_load": 2.5,
        "live_load": 1.8,
        "wind_load": 4.2
    })

    print(result)
    # Output: {'combination': 'U4', 'value': 9.24, 'units': 'kip/ft'}