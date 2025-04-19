class AppException(Exception):
    """Excepción base para errores de la aplicación."""

    def __init__(self, detail: str = "An application error occurred."):
        self.detail = detail
        super().__init__(self.detail)


class ResourceNotFound(AppException):
    """Recurso no encontrado (ej: URL con ID específico)."""

    def __init__(self, resource: str = "Resource", identifier: str = "provided ID"):
        detail = f"{resource} not found for {identifier}."
        super().__init__(detail)


class DatabaseError(AppException):
    """Error relacionado con la base de datos."""

    def __init__(
        self,
        detail: str = "A database error occurred.",
        original_exception: Exception | None = None,
    ):
        self.original_exception = original_exception
        super().__init__(detail)


class ValidationError(AppException):
    """Error de validación de datos."""

    def __init__(self, detail: str = "Invalid data provided."):
        super().__init__(detail)


class OperationError(AppException):
    """Error al realizar una operación específica."""

    def __init__(self, operation: str = "Operation", detail: str = "failed"):
        full_detail = f"{operation} {detail}"
        super().__init__(full_detail)
