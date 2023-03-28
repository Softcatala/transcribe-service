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

whisper-models:
	if [ ! -d "models" ]; then \
		git clone --depth 1 https://huggingface.co/datasets/jordimas/whisper-ct2-v2 models ;\
		cd models && git lfs pull ;\
		rm *-en* -r -f && rm *large* -r -f && rm *base* -r -f && rm *tiny* -r -f && rm .git/* -r -f ;\
	fi

benchmark-samples:
	mkdir -p benchmark
	if [ ! -d "benchmark/samples" ]; then git clone --depth 1 https://gitlab.softcatala.org/nous-projectes/catalan-audio-samples.git/ benchmark/samples; fi

benchmark-run: whisper.cpp whisper.cpp-models benchmark-samples
	cd benchmark && python3 whispercpp.py
