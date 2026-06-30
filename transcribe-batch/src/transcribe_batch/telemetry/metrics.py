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
meter = metrics.get_meter("transcribe-batch")

processed_files_counter = meter.create_counter(
    "files_processed_total",
    unit="1",
    description="Total files processed by model and result",
)

audio_conversion_histogram = meter.create_histogram(
    "audio_conversion_duration_seconds",
    unit="s",
    description="Time taken to convert an audio file using Ffmpeg or Sox.",
)

whisper_inference_histogram = meter.create_histogram(
    "whisper_inference_duration_seconds",
    unit="s",
    description="Time taken by whisper to transcribe an audio file by model.",
)

language_detected_counter = meter.create_counter(
    "language_detected_total",
    unit="1",
    description="Total detected audio files by language.",
)
