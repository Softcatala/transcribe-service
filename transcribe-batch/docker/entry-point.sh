#!/bin/sh

if [ ! -z "$LOGDIR" ]
then
    mkdir -p $LOGDIR
fi
uv run src/transcribe_batch/main.py
