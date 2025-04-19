import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler

# --- Configuración ---
LOG_LEVEL = os.getenv(
    "LOG_LEVEL", "INFO"
).upper()  # Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(process)d:%(thread)d - %(filename)s:%(lineno)d - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# --- Opcional: Log a archivo ---
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() == "true"
LOG_FILE_PATH = os.getenv(
    "LOG_FILE_PATH", "logs/app.log"
)  # Directorio 'logs' en la raíz del backend
LOG_FILE_WHEN = "midnight"  # Rotar archivos diariamente
LOG_FILE_INTERVAL = 1
LOG_FILE_BACKUP_COUNT = 7  # Mantener logs de 7 días

# --- Crear directorio de logs si no existe (si se loguea a archivo) ---
if LOG_TO_FILE:
    log_dir = os.path.dirname(LOG_FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)


def setup_logging():
    """Configura el logging para la aplicación."""
    # Crear formateador
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Configurar el logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    root_logger.handlers.clear()  # Limpiar handlers preexistentes (importante en reload)

    # Handler para la consola (siempre activo)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(LOG_LEVEL)  # Nivel para la consola
    root_logger.addHandler(console_handler)

    # Handler para archivo (opcional)
    if LOG_TO_FILE:
        file_handler = TimedRotatingFileHandler(
            LOG_FILE_PATH,
            when=LOG_FILE_WHEN,
            interval=LOG_FILE_INTERVAL,
            backupCount=LOG_FILE_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(LOG_LEVEL)  # Nivel para el archivo
        root_logger.addHandler(file_handler)
        root_logger.info(f"Logging to file enabled: {LOG_FILE_PATH}")

    # Silenciar loggers de librerías muy verbosas si es necesario
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING
    )  # O INFO/DEBUG si necesitas ver queries

    root_logger.info(f"Logging setup complete. Level: {LOG_LEVEL}")


# --- Llamar a setup_logging() aquí asegura que se configure al importar ---
# setup_logging() # Alternativa: Llamarlo explícitamente en main.py
