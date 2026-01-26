class ServiceException(Exception):
    def __init__(
        self,
        message: str = "Request error.",
        errors: dict = {},
        code: int = 400,
    ) -> None:
        self.message = message
        self.errors = errors
        self.code = code
