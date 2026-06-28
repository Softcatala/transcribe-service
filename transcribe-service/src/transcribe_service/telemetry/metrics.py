import asyncio
from pathlib import Path

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.view import (
    ExplicitBucketHistogramAggregation,
    View,
)
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from transcribe_core.batchfilesdb import BatchFilesDB

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(), export_interval_millis=5000
)

file_size_buckets = View(
    instrument_name="uploaded_transcription_size_bytes",
    aggregation=ExplicitBucketHistogramAggregation(
        boundaries=[
            0,
            100,
            500,
            1000,
            5000,
            10000,
            50000,
            100000,
            500_000,
            1_000_000,
            5_000_000,
            10_000_000,
            50_000_000,
            100_000_000,
            250_000_000,
            500_000_000,
            750_000_000,
            1_000_000_000,
        ],
    ),
)

provider = MeterProvider(metric_readers=[reader], views=[file_size_buckets])

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

queue_depth_gauge = meter.create_gauge(
    "queue_depth",
    unit="1",
    description="Current total entries in queue (waiting + processing)",
)

currently_processing_transcriptions_gauge = meter.create_gauge(
    "in_process_transcriptions",
    unit="1",
    description="Current transcriptions being processed (active lock files)",
)


async def _update_queue_depth() -> None:
    while True:
        queue_depth_gauge.set(BatchFilesDB().count())
        await asyncio.sleep(5)


async def _reconcile_in_process() -> None:
    ENTRIES_DIR = Path("/srv/data/entries")
    while True:
        processing = len(list(ENTRIES_DIR.glob("*.lock")))  # noqa: ASYNC240
        currently_processing_transcriptions_gauge.set(processing)
        await asyncio.sleep(60)
