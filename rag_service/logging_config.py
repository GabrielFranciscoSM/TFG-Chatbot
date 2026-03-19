import logging
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime

from fastapi import Request
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable to store the correlation ID for the current request
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            # Use ISO 8601 format for timestamps
            now = datetime.now(UTC).isoformat()
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname

        # Add correlation ID from context
        log_record["correlation_id"] = correlation_id_ctx.get()
        # Add service name
        log_record["service"] = "rag_service"


def setup_logging(level=logging.INFO):
    """Setup structured JSON logging."""
    logger = logging.getLogger()
    logger.setLevel(level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    handler = logging.StreamHandler()
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s %(correlation_id)s %(service)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent logs from propagating to the root logger if it's already configured
    logger.propagate = False


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to extract or generate a correlation ID for each request."""

    async def dispatch(self, request: Request, call_next):
        # Try to get correlation ID from headers, or generate a new one
        corr_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

        # Set the correlation ID in the context
        token = correlation_id_ctx.set(corr_id)

        try:
            response = await call_next(request)
            # Return the correlation ID in the response headers
            response.headers["X-Correlation-ID"] = corr_id
            return response
        finally:
            # Reset the context variable
            correlation_id_ctx.reset(token)
