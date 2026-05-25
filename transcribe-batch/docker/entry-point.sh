#!/bin/sh

if [ ! -z "$LOGDIR" ]
then
    mkdir -p $LOGDIR
fi
uv run --no-sync src/transcribe_batch/main.py
