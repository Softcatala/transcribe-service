if [ ! -z "$LOGDIR" ]
then
    mkdir -p $LOGDIR
fi
python3 process-batch.py
