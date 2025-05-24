import docker
# 호스트 Docker 데몬과 통신하는 client 객체
try:
    client = docker.from_env()
except docker.errors.DockerException:
    print("Docker 데몬에 연결할 수 없습니다. Docker가 실행 중인지 확인하세요.")
    client = None