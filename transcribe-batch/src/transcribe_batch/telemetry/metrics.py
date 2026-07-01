from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(), export_interval_millis=5000
)
provider = MeterProvider(metric_readers=[reader])

metrics.set_meter_provider(provider)
meter = metrics.get_meter("transcribe-batch")

processed_files_counter = meter.create_counter(
    "files_processed_total",
    unit="1",
    description="Total files processed by model and result",
)

transcription_duration_histogram = meter.create_histogram(
    "transcription_duration_seconds",
    unit="s",
    description="Time taken to transcribe a file (from start of conversion to end of inference) by model",
)

language_detected_counter = meter.create_counter(
    "language_detected_total",
    unit="1",
    description="Total detected audio files by language.",
)
