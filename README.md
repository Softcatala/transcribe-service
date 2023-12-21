# Introduction

The transcribe-service provides the following functionality:
* Receives files and creates a priortized queue to serve them
* Notifies by email when file is ready or it has been error
* Provides an estimated time for the file to be ready

The requirements of the system is to process a file at the time, a maximum 100 files in queue to be processed and ability to easily
to change the transcribe tool and models that we use.

# Description of system

The transcribe web service exposes the POST method */transcribe_file/*. From the web site, the user sends an audio or video that they
want to transcribe. This file is then stored in queue that is processed by order of arrival. Once the processing finished, an
email is sent to the user to download the resulting files.

## Queue

This is a priority queue implemented on top of the fileystem. 

The files to be processed by the queue are stored in */srv/files/* and a entry in */srv/entries/* is created with the
information received on the POST. Once the files are transcribed the results are stored into /srv/processed for the 
user to pick resulting files. The web services exposes the method *get_file* which then serves files from the processed directories.

Elements on the processed directory are purged after certain amound of time.

## Estimation

The system keeps record of how much time each filetype (mp3, mp4, etc) was needed to transcribe it. It builds a ratio of MB/s which the
system can process than it's used to estimate future files. The sample data points used to calculated this are the last ones, then if
the hardware, version of the transcription tool or other external factor changes, the system will self-adjust based on the time need
to do recent transcriptions.


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

# Updating faster-whisper dependency

Updating dependencies to a newer version or test new models.

Then run the benchmark:

```shell
make benchmark-run
```

And make sure that there is no regression in WER (precision) or time (latency) in the *results.json* file.


# Contact

Email address: Jordi Mas: jmas@softcatala.org

