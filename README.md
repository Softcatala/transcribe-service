# transcribe-service

# Running the system locally using Docker

This requires that you have *docker*, *docker-compose* and *make* installed in your system.

First build by running:

```shell
 make build-all
```

Once the system is built, you can run it typing:

```shell
docker-run
```

And open http://localhost:8700/hello to verify that the service works.

Also in the [html-client](html-client) directory you have a simple HTML client to test the service.

# Updating whisper.cpp dependency

Updating whisper.cpp dependency to a newer version.


In the [Makefile](Makefile) file, update the *whisper.cpp* task with right tag to do *git clone*.

Then run the benchmark:

```shell
make benchmark-run
```

And make sure that there is no regression in WER (precission) or time (latency) in the *results.json* file.
