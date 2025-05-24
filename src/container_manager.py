import docker, socket, random, uuid
from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel

# APIRouter 인스턴스 생성
router = APIRouter()
client = docker.from_env()

# 문제별 포트 범위 매핑 (최소, 최대)
PROBLEM_PORT_RANGES = {
    1: (2000, 5000),
    2: (3000, 8000),
    3: (3000, 8000),
    4: (2000, 6000),
    5: (2000, 6000),
    6: (2000, 6000),
    7: (2000, 6000),
    8: (2000, 6000),
    9: (2000, 6000),
    10: (2000, 6000),
}

# 문제 ID와 이미지 이름 매핑
PROBLEM_IMAGE_NAMES = {
    1: "csrf",
    2: "sqli2",
    3: "sqli3",
    4: "command",
    5: "stored_xss_1",
    6: "stored_xss_2",
    7: "stored_xss_3",
    8: "reflected_xss",
    9: "file-upload",
    10: "path-traversal",
}

# 실행 중인 인스턴스 정보 저장
_instances: dict[str, dict] = {}
# 문제별 활성 인스턴스 맵 (problem_id -> instance_id)
_active_by_problem: dict[int, str] = {}

class StartRequest(BaseModel):
    problem_id: int

class StartResponse(BaseModel):
    instance_id: str
    backend_host: str
    backend_port: int
    frontend_host: str
    frontend_port: int
    network: str
    frontend_url: str

class StopResponse(BaseModel):
    instance_id: str
    message: str


def _find_available_port(port_range: tuple[int, int]) -> int:
    """주어진 범위에서 사용 가능한 포트를 랜덤하게 검색"""
    start, end = port_range
    for _ in range(50):
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise RuntimeError("사용 가능한 포트를 찾을 수 없습니다.")

@router.post("/start", response_model=StartResponse)
def start_problem(req: StartRequest):
    pid = req.problem_id
    if pid not in PROBLEM_IMAGE_NAMES:
        raise HTTPException(status_code=400, detail="유효하지 않은 문제 ID입니다.")
    # 이미 실행된 인스턴스가 있으면 중단 후 재실행
    if pid in _active_by_problem:
        _cleanup_instance(_active_by_problem[pid])

    image_name = PROBLEM_IMAGE_NAMES[pid]
    port_range = PROBLEM_PORT_RANGES[pid]

    backend_port = _find_available_port(port_range)
    frontend_port = _find_available_port(port_range)
    while frontend_port == backend_port:
        frontend_port = _find_available_port(port_range)

    # 네트워크 생성
    network_name = f"problem_{pid}_{uuid.uuid4().hex[:8]}"
    network = client.networks.create(network_name, driver="bridge")

    # 컨테이너 실행
    backend_container = client.containers.run(
        f"zeroday01478/{image_name}:backend",
        detach=True,
        name=f"{network_name}_backend",
        ports={"8000/tcp": backend_port},
        network=network_name,
    )
    frontend_container = client.containers.run(
        f"zeroday01478/{image_name}:frontend",
        detach=True,
        name=f"{network_name}_frontend",
        ports={"80/tcp": frontend_port},
        network=network_name,
    )

    instance_id = uuid.uuid4().hex
    _instances[instance_id] = {
        "network": network,
        "backend": backend_container,
        "frontend": frontend_container,
    }
    _active_by_problem[pid] = instance_id

    # frontend URL 조합
    frontend_url = f"http://{frontend_container.attrs['NetworkSettings']['IPAddress']}:{frontend_port}" if False else f"http://{"localhost"}:{frontend_port}"

    return StartResponse(
        instance_id=instance_id,
        backend_host="localhost",
        backend_port=backend_port,
        frontend_host="localhost",
        frontend_port=frontend_port,
        network=network_name,
        frontend_url=frontend_url,
    )

@router.post("/stop/{instance_id}", response_model=StopResponse)
def stop_problem(instance_id: str):
    return _stop_and_cleanup(instance_id)

@router.post("/stop_by_problem/{problem_id}", response_model=StopResponse)
def stop_by_problem(problem_id: int):
    if problem_id not in _active_by_problem:
        raise HTTPException(status_code=404, detail="해당 문제 실행 인스턴스가 없습니다.")
    instance_id = _active_by_problem[problem_id]
    return _stop_and_cleanup(instance_id)

@router.get("/instances")
def list_instances():
    """현재 실행 중인 인스턴스 목록"""
    return {pid: _active_by_problem[pid] for pid in _active_by_problem}


def _cleanup_instance(instance_id: str):
    data = _instances.get(instance_id)
    if not data:
        return
    try:
        data["backend"].stop(); data["backend"].remove()
        data["frontend"].stop(); data["frontend"].remove()
    except:
        pass
    try:
        data["network"].remove()
    except:
        pass
    _instances.pop(instance_id, None)
    for pid, iid in list(_active_by_problem.items()):
        if iid == instance_id:
            _active_by_problem.pop(pid)


def _stop_and_cleanup(instance_id: str) -> StopResponse:
    if instance_id not in _instances:
        raise HTTPException(status_code=404, detail="찾을 수 없는 인스턴스 ID입니다.")
    _cleanup_instance(instance_id)
    return StopResponse(instance_id=instance_id, message="인스턴스가 정상적으로 종료되었습니다.")
