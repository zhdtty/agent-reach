class RustChainError(Exception):
    pass

class APIError(RustChainError):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"APIError[{status_code}]: {message}")

class NotFoundError(APIError):
    pass

class ValidationError(RustChainError):
    pass
