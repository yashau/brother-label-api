"""
OpenTelemetry metrics configuration and instrumentation
Exports metrics via OTLP HTTP to configured endpoint (e.g., Grafana Cloud)
"""

import os
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource


class TelemetryManager:
    """Manages OpenTelemetry metrics for the Brother Label API"""

    def __init__(self):
        self.enabled = os.getenv('OTEL_ENABLED', 'false').lower() == 'true'

        if not self.enabled:
            # Create no-op metrics
            self._setup_noop_metrics()
            return

        # Configure OTLP exporter
        endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
        headers = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')

        if not endpoint:
            print("Warning: OTEL_ENABLED=true but OTEL_EXPORTER_OTLP_ENDPOINT not set. Metrics disabled.")
            self._setup_noop_metrics()
            return

        # Parse headers (format: "key1=value1,key2=value2")
        headers_dict = {}
        if headers:
            for header in headers.split(','):
                if '=' in header:
                    key, value = header.split('=', 1)
                    headers_dict[key.strip()] = value.strip()

        # Create resource with service information
        resource = Resource.create({
            "service.name": os.getenv('OTEL_SERVICE_NAME', 'brother-label-api'),
            "service.version": "0.9.5.1",
            "deployment.environment": os.getenv('OTEL_ENVIRONMENT', 'production'),
        })

        # Configure exporter
        exporter = OTLPMetricExporter(
            endpoint=endpoint,
            headers=headers_dict,
        )

        # Create metric reader with export interval
        reader = PeriodicExportingMetricReader(
            exporter=exporter,
            export_interval_millis=int(os.getenv('OTEL_EXPORT_INTERVAL_MS', '60000'))
        )

        # Set up meter provider
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[reader]
        )
        metrics.set_meter_provider(meter_provider)

        # Get meter for this service
        self.meter = metrics.get_meter(__name__)

        # Initialize all metrics
        self._setup_metrics()

    def _setup_noop_metrics(self):
        """Create no-op metrics when telemetry is disabled"""
        # Get default meter (no-op)
        self.meter = metrics.get_meter(__name__)
        self._setup_metrics()

    def _setup_metrics(self):
        """Initialize all metrics (counters, histograms, gauges)"""

        # === COUNTERS ===
        self.api_requests_counter = self.meter.create_counter(
            name="api.requests.total",
            description="Total number of API requests",
            unit="1"
        )

        self.prints_total_counter = self.meter.create_counter(
            name="prints.total",
            description="Total number of print jobs attempted",
            unit="1"
        )

        self.prints_success_counter = self.meter.create_counter(
            name="prints.success",
            description="Total number of successful print jobs",
            unit="1"
        )

        self.prints_failed_counter = self.meter.create_counter(
            name="prints.failed",
            description="Total number of failed print jobs",
            unit="1"
        )

        self.errors_counter = self.meter.create_counter(
            name="errors.total",
            description="Total number of errors by type",
            unit="1"
        )

        # === HISTOGRAMS ===
        self.http_request_duration = self.meter.create_histogram(
            name="http.request.duration",
            description="HTTP request duration in milliseconds",
            unit="ms"
        )

        self.print_duration = self.meter.create_histogram(
            name="print.duration",
            description="Print job duration in milliseconds",
            unit="ms"
        )

        self.image_generation_duration = self.meter.create_histogram(
            name="image.generation.duration",
            description="Image generation duration in milliseconds",
            unit="ms"
        )

        self.printer_response_time = self.meter.create_histogram(
            name="printer.response.time",
            description="Printer response time in milliseconds",
            unit="ms"
        )

        # === GAUGES (using observable callbacks) ===
        self._printers_configured = 0
        self._api_keys_configured = 0

        self.meter.create_observable_gauge(
            name="printers.configured",
            description="Number of configured printers",
            unit="1",
            callbacks=[self._get_printers_configured]
        )

        self.meter.create_observable_gauge(
            name="api_keys.configured",
            description="Number of configured API keys",
            unit="1",
            callbacks=[self._get_api_keys_configured]
        )

    def _get_printers_configured(self, options):
        """Callback for printers.configured gauge"""
        yield metrics.Observation(self._printers_configured)

    def _get_api_keys_configured(self, options):
        """Callback for api_keys.configured gauge"""
        yield metrics.Observation(self._api_keys_configured)

    def update_config_gauges(self, printers_count: int, api_keys_count: int):
        """Update gauge values for configuration counts"""
        self._printers_configured = printers_count
        self._api_keys_configured = api_keys_count

    # === Helper Methods ===

    def record_api_request(self, endpoint: str, method: str, status_code: int,
                          api_key_name: Optional[str] = None):
        """Record an API request"""
        attributes = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
        }
        if api_key_name:
            attributes["api_key_name"] = api_key_name

        self.api_requests_counter.add(1, attributes)

    def record_print_attempt(self, printer_id: str, printer_model: str,
                            label_type: str, api_key_name: Optional[str] = None):
        """Record a print job attempt"""
        attributes = {
            "printer_id": printer_id,
            "printer_model": printer_model,
            "label_type": label_type,
        }
        if api_key_name:
            attributes["api_key_name"] = api_key_name

        self.prints_total_counter.add(1, attributes)

    def record_print_success(self, printer_id: str, printer_model: str,
                            label_type: str, duration_ms: float,
                            api_key_name: Optional[str] = None):
        """Record a successful print job"""
        attributes = {
            "printer_id": printer_id,
            "printer_model": printer_model,
            "label_type": label_type,
        }
        if api_key_name:
            attributes["api_key_name"] = api_key_name

        self.prints_success_counter.add(1, attributes)
        self.print_duration.record(duration_ms, {
            "printer_id": printer_id,
            "printer_model": printer_model,
            "result": "success"
        })

    def record_print_failure(self, printer_id: str, printer_model: str,
                            error_type: str, duration_ms: float,
                            api_key_name: Optional[str] = None):
        """Record a failed print job"""
        attributes = {
            "printer_id": printer_id,
            "printer_model": printer_model,
            "error_type": error_type,
        }
        if api_key_name:
            attributes["api_key_name"] = api_key_name

        self.prints_failed_counter.add(1, attributes)
        self.print_duration.record(duration_ms, {
            "printer_id": printer_id,
            "printer_model": printer_model,
            "result": "failure"
        })

    def record_error(self, error_type: str, endpoint: str,
                    api_key_name: Optional[str] = None):
        """Record an error"""
        attributes = {
            "error_type": error_type,
            "endpoint": endpoint,
        }
        if api_key_name:
            attributes["api_key_name"] = api_key_name

        self.errors_counter.add(1, attributes)

    def record_http_duration(self, duration_ms: float, endpoint: str,
                            method: str, status_code: int):
        """Record HTTP request duration"""
        self.http_request_duration.record(duration_ms, {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code
        })

    def record_image_generation(self, duration_ms: float, label_type: str):
        """Record image generation duration"""
        self.image_generation_duration.record(duration_ms, {
            "label_type": label_type
        })

    def record_printer_response(self, duration_ms: float, printer_id: str,
                               printer_model: str):
        """Record printer response time"""
        self.printer_response_time.record(duration_ms, {
            "printer_id": printer_id,
            "printer_model": printer_model
        })

    @contextmanager
    def measure_duration(self):
        """Context manager to measure duration in milliseconds"""
        start = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start) * 1000


# Global telemetry instance
_telemetry: Optional[TelemetryManager] = None


def init_telemetry() -> TelemetryManager:
    """Initialize telemetry (call once at application startup)"""
    global _telemetry
    if _telemetry is None:
        _telemetry = TelemetryManager()
    return _telemetry


def get_telemetry() -> TelemetryManager:
    """Get the global telemetry instance"""
    if _telemetry is None:
        return init_telemetry()
    return _telemetry
