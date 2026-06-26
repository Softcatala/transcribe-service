from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(), export_interval_millis=5000
)
provider = MeterProvider(metric_readers=[reader])

metrics.set_meter_provider(provider)
meter = metrics.get_meter("transcribe-service")

uploads_counter = meter.create_counter(
    "transcriptions_uploaded_total",
    unit="1",
    description="Total uploads by model, email and result",
)

downloads_counter = meter.create_counter(
    "transcriptions_downloaded_total",
    unit="1",
    description="Total downloads by extension and result",
)

deleted_counter = meter.create_counter(
    "transcriptions_manually_deleted_total",
    unit="1",
    description="Total deleted by uuid and result",
)

uploaded_file_size_histogram = meter.create_histogram(
    "uploaded_transcription_size_bytes",
    unit="bytes",
    description="Size of uploaded transcription files.",
)
