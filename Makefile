build-all: docker-build-transcribe-service docker-build-transcribe-batch

docker-build-transcribe-service:
	docker build -t transcribe-service . -f transcribe-service/docker/Dockerfile;

docker-build-transcribe-batch:
	docker build -t transcribe-batch . -f transcribe-batch/docker/Dockerfile;

