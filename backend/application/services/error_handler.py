import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import (
    RequestValidationError,
)
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,
)

from domain.exceptions import (
    AppException,
    ResourceNotFound,
    DatabaseError,
    ValidationError,
)


logger = logging.getLogger(__name__)


async def handle_app_exception(request: Request, exc: AppException):
    """Manejador genérico para nuestras excepciones personalizadas."""
    logger.error(
        f"Application error occurred: {exc.detail}", exc_info=True
    )  # Log con traceback
    # Por defecto, las excepciones de app podrían ser 400 o 500 dependiendo del tipo
    # Aquí usamos 400 como un ejemplo general, pero se puede refinar
    status_code = status.HTTP_400_BAD_REQUEST
    if isinstance(exc, ResourceNotFound):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DatabaseError):
        status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
        )  # O 500 si es un error interno inesperado
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY  # O 400

    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.detail},
    )


async def handle_validation_exception(request: Request, exc: RequestValidationError):
    """Manejador para errores de validación de Pydantic."""
    # exc.errors() da detalles sobre qué campo falló la validación
    logger.warning(
        f"Request validation error: {exc.errors()}", exc_info=False
    )  # No necesitamos traceback completo usualmente
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": exc.errors()},
    )


async def handle_http_exception(request: Request, exc: StarletteHTTPException):
    """Manejador para excepciones HTTPException estándar de FastAPI/Starlette."""
    # Estas ya tienen status_code y detail
    logger.warning(f"HTTP exception occurred: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )


async def handle_generic_exception(request: Request, exc: Exception):
    """Manejador para cualquier otra excepción no capturada (errores 500)."""
    logger.critical(
        f"Unhandled exception occurred: {exc}", exc_info=True
    )  # Log como CRITICAL con traceback
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal Server Error"
        },  # No exponer detalles internos al cliente
    )


def register_exception_handlers(app: FastAPI):
    """Registra todos los manejadores de excepciones en la app FastAPI."""
    app.add_exception_handler(
        AppException, handle_app_exception
    )  # Base para nuestras excepciones
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(
        Exception, handle_generic_exception
    )  # Captura todo lo demás
    logger.info("Custom exception handlers registered.")
