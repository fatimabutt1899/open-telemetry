from flask import Flask, request
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
import logging

# Azure Application Insights Connection String
CONNECTION_STRING ="Add-Your-String"

# --- OpenTelemetry Setup ---
# Tracing Setup
trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": "azure-otel-test-app"})))
tracer_provider = trace.get_tracer_provider()
trace_exporter = AzureMonitorTraceExporter(connection_string=CONNECTION_STRING)
tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

# Metrics Setup
metric_exporter = AzureMonitorMetricExporter(connection_string=CONNECTION_STRING)
meter_provider = MeterProvider(
    resource=Resource.create({"service.name": "azure-otel-test-app"}),
    metric_readers=[PeriodicExportingMetricReader(metric_exporter)]
)
metrics.set_meter_provider(meter_provider)
meter = meter_provider.get_meter(__name__)
request_counter = meter.create_counter("request_count", description="Number of requests served")

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Flask App ---
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)


@app.route("/")
def home():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("home-page-span") as span:
        span.set_attribute("route", "/")
        span.add_event("Serving home page")
        logger.info("Accessed home page")
        request_counter.add(1, {"route": "/"})
        return "Hello from OpenTelemetry with Azure!"


@app.route("/test")
def test():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("test-page-span") as span:
        number = int(request.args.get("number", 0))
        span.set_attribute("input_number", number)
        span.add_event("Performing square calculation")
        result = number ** 2
        span.set_attribute("result", result)
        request_counter.add(1, {"route": "/test"})
        logger.info(f"Processed number {number}, result: {result}")
        return {"result": result}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
