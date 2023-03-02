.PHONY: docker-build-transcribe-models docker-build-transcribe-service docker-build-transcribe-batch docker-run test whisper.cpp whisper.cpp-models benchmark-run benchmark-run

build-all: docker-build-transcribe-models docker-build-transcribe-service docker-build-transcribe-batch

docker-build-transcribe-models:
	docker build -t transcribe-models . -f transcribe-batch/docker/Dockerfile-models;
	
docker-build-transcribe-service:
	docker build -t transcribe-service . -f transcribe-service/docker/Dockerfile;

docker-build-transcribe-batch: docker-build-transcribe-models
	docker build -t transcribe-batch . -f transcribe-batch/docker/Dockerfile;

docker-run:
	docker-compose -f local.yml up;

test:
	cd transcribe-batch && python -m nose2

whisper.cpp:
	if [ ! -d "whisper.cpp" ]; then git clone --branch v1.2.1 https://github.com/ggerganov/whisper.cpp; fi
	cd whisper.cpp &&  make

whisper.cpp-models:
	if [ ! -d "whisper.cpp/sc-models" ]; then git clone --depth 1 https://gitlab.softcatala.org/jmas/whisper.cpp-models.git/ whisper.cpp/sc-models; fi
	cd whisper.cpp/sc-models && git lfs pull

benchmark-samples:
	mkdir -p benchmark
	if [ ! -d "benchmark/samples" ]; then git clone --depth 1 https://gitlab.softcatala.org/nous-projectes/catalan-audio-samples.git/ benchmark/samples; fi

benchmark-run: whisper.cpp whisper.cpp-models benchmark-samples
	cd benchmark && python3 whispercpp.py
