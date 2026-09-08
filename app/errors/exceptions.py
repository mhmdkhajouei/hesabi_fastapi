class AppError(Exception):
    def __init__(self, status_code: int, message: str, error_code: str):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code

        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str, error_code: str = "NOT_FOUND"):
        super().__init__(message=message, status_code=404, error_code=error_code)


class BusinessRuleError(AppError):
    def __init__(self, message: str, error_code: str = "BUSINESS_RULE_ERROR"):
        super().__init__(message=message, status_code=422, error_code=error_code)


class AuthenticationError(AppError):
    def __init__(self, message: str, error_code: str = "AUTHENTICATION_FAILED"):
        super().__init__(message=message, status_code=401, error_code=error_code)
