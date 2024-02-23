.PHONY: docker-build-transcribe-models docker-build-transcribe-service docker-build-transcribe-batch docker-run test whisper-models benchmark-run

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
	python3 -c 'from faster_whisper import WhisperModel; WhisperModel("small");  WhisperModel("medium")'

benchmark-samples:
	mkdir -p benchmark
	if [ ! -d "benchmark/samples" ]; then git clone --depth 1 https://gitlab.softcatala.org/nous-projectes/catalan-audio-samples.git/ benchmark/samples; fi

benchmark-run: whisper-models benchmark-samples
#	pip install evaluate jiwer
	cd benchmark && python3 whisper.py
	@python3 -c 'import faster_whisper; print(f"faster_whisper: {faster_whisper.__version__}")'
	@python3 -c 'import ctranslate2; print(f"ctranslate2: {ctranslate2.__version__}")'
	@whisper-ctranslate2 --version
