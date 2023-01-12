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

