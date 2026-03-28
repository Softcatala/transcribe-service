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
from prometheus_client import generate_latest, REGISTRY
from telemetry import MEM_GAUGE, UPTIME_GAUGE
import psutil
import time

metrics_bp = Blueprint("metrics", __name__)

# Store startup time for uptime calculation
_startup_time = None


def init_metrics(app):
    """Initialize metrics with Flask app context"""
    global _startup_time
    _startup_time = time.time()
    app.register_blueprint(metrics_bp)


@metrics_bp.route("/metrics", methods=["GET"])
def metrics():
    """Expose Prometheus metrics"""
    # Update memory usage gauge
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    MEM_GAUGE.set(memory_mb)

    # Update uptime gauge
    if _startup_time:
        uptime = time.time() - _startup_time
        UPTIME_GAUGE.set(uptime)

    return Response(generate_latest(REGISTRY), mimetype="text/plain")
