#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2022-2023 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

from flask import Blueprint, Response
from prometheus_client import generate_latest, CollectorRegistry, multiprocess
from telemetry import MEM_GAUGE, UPTIME_GAUGE
import psutil
import time
import os

metrics_bp = Blueprint("metrics", __name__)

# Store startup time for uptime calculation
_startup_time = None


def init_metrics(app):
    """Initialize metrics with Flask app context"""
    global _startup_time
    _startup_time = time.time()
    app.register_blueprint(metrics_bp)


def _read_batch_metrics():
    """Read batch metrics from file if it exists"""
    logdir = os.environ.get("LOGDIR", "/tmp")
    batch_metrics_file = os.path.join(logdir, "batch_metrics.txt")
    try:
        if os.path.exists(batch_metrics_file):
            with open(batch_metrics_file, "r") as f:
                return f.read()
    except Exception:
        pass
    return ""


@metrics_bp.route("/metrics", methods=["GET"])
def metrics():
    """Expose Prometheus metrics including batch metrics"""
    # Update memory usage gauge
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    MEM_GAUGE.set(memory_mb)

    # Update uptime gauge
    if _startup_time:
        uptime = time.time() - _startup_time
        UPTIME_GAUGE.set(uptime)

    # Get web service metrics - use multiprocess collector when running under gunicorn
    if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
    else:
        from prometheus_client import REGISTRY as registry
    web_metrics = generate_latest(registry).decode("utf-8")

    # Get batch metrics if available
    batch_metrics = _read_batch_metrics()

    # Combine metrics
    all_metrics = web_metrics + "\n" + batch_metrics if batch_metrics else web_metrics

    return Response(all_metrics, mimetype="text/plain")
