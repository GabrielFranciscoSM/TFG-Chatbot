"""Phoenix/OpenInference instrumentation for LLM observability.

This module configures tracing for LangChain/LangGraph components using
OpenInference instrumentation, sending traces to a Phoenix collector.
"""

import logging
from functools import cache

from chatbot.config import settings

logger = logging.getLogger(__name__)


@cache
def setup_phoenix_instrumentation() -> bool:
    """Initialize Phoenix/OpenInference instrumentation.

    This function is cached to ensure instrumentation is only set up once.

    Returns:
        True if instrumentation was set up successfully, False otherwise.
    """
    if not settings.phoenix_enabled:
        logger.info("Phoenix instrumentation disabled via PHOENIX_ENABLED=false")
        return False

    try:
        from openinference.instrumentation.langchain import LangChainInstrumentor
        from openinference.semconv.resource import ResourceAttributes
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor

        # Configure the OTLP exporter to send traces to Phoenix
        phoenix_endpoint = (
            f"http://{settings.phoenix_host}:{settings.phoenix_port}/v1/traces"
        )

        # Phoenix uses ResourceAttributes.PROJECT_NAME to group traces
        resource = Resource(
            attributes={ResourceAttributes.PROJECT_NAME: settings.phoenix_project_name}
        )

        tracer_provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=phoenix_endpoint)
        tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
        trace.set_tracer_provider(tracer_provider)

        # Instrument LangChain
        LangChainInstrumentor().instrument()

        logger.info(
            "Phoenix instrumentation enabled, project=%s, endpoint=%s",
            settings.phoenix_project_name,
            phoenix_endpoint,
        )
        return True

    except ImportError as e:
        logger.warning("Phoenix instrumentation dependencies not available: %s", e)
        return False
    except Exception as e:
        logger.error("Failed to set up Phoenix instrumentation: %s", e)
        return False
