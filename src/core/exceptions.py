class RCBeamError(Exception):
    """Base exception for RC beam system"""
    pass

class DesignError(RCBeamError):
    """Raised when design calculations fail"""
    def __init__(self, step: str, message: str):
        self.step = step
        self.message = message
        super().__init__(f"Design error in {step}: {message}")

class VerificationError(RCBeamError):
    """Raised when verification fails"""
    def __init__(self, step: str, message: str):
        self.step = step
        self.message = message
        super().__init__(f"Verification error in {step}: {message}")

class InputError(RCBeamError):
    """Raised for invalid inputs"""
    def __init__(self, parameter: str, message: str):
        self.parameter = parameter
        self.message = message
        super().__init__(f"Invalid input parameter '{parameter}': {message}")