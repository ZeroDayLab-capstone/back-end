import uuid
import asyncio

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from docker_client import client
from docker_utils import find_free_port
from config import PROBLEM_CONFIGS, PROBLEM_FLAGS

router = APIRouter()

_instances: dict[str, dict] = {}
_active_by_problem: dict[int, str] = {}

class StartRequest(BaseModel):
    problem_id: int

class StartResponse(BaseModel):
    instance_id: str
    frontend_url: str
    backend_port: int
    frontend_port: int
    network: str

class StopResponse(BaseModel):
    instance_id: str
    message: str

async def _auto_cleanup(instance_id: str, ttl_sec: int = 3600):
    await asyncio.sleep(ttl_sec)
    _cleanup(instance_id)


def _cleanup(instance_id: str):
    data = _instances.pop(instance_id, None)
    if not data:
        return
    # 컨테이너 정리
    for role in ("backend", "frontend"):
        ctr = data.get(role)
        if ctr:
            try:
                ctr.stop(timeout=5)
                ctr.remove(force=True, v=True)
            except Exception:
                pass
    # 네트워크 삭제
    try:
        data["network"].remove()
    except Exception:
        pass
    # 매핑 제거
    for pid, iid in list(_active_by_problem.items()):
        if iid == instance_id:
            _active_by_problem.pop(pid)

@router.post("/start", response_model=StartResponse)
async def start_problem(req: StartRequest):
    pid = req.problem_id
    cfg = PROBLEM_CONFIGS.get(pid)
    if not cfg:
        raise HTTPException(400, "유효하지 않은 문제 ID입니다.")

    # 호스트 포트 할당
    b_port = find_free_port(cfg["host_range"])
    f_port = find_free_port(cfg["host_range"])
    while f_port == b_port:
        f_port = find_free_port(cfg["host_range"])

    # 네트워크 생성
    net = client.networks.create(f"prob_{pid}_{uuid.uuid4().hex[:8]}", driver="bridge")
    be_name = f"{net.name}_be"
    fe_name = f"{net.name}_fe"

    # 백엔드 실행
    try:
        backend = client.containers.run(
            cfg["backend_image"], name=be_name, detach=True,
            network=net.name, ports={f"{cfg['backend_port']}/tcp": b_port},
            environment={"FLAG": PROBLEM_FLAGS[pid]}
        )
    except Exception as e:
        net.remove()
        raise HTTPException(500, f"백엔드 실행 실패: {e}")

    # 프론트엔드 실행
    try:
        frontend = client.containers.run(
            cfg["frontend_image"], name=fe_name, detach=True,
            network=net.name, ports={f"{cfg['frontend_port']}/tcp": f_port},
            environment={"API_URL": f"http://{be_name}:{cfg['backend_port']}"}
        )
    except Exception as e:
        backend.stop(timeout=5)
        backend.remove(force=True, v=True)
        net.remove()
        raise HTTPException(500, f"프론트엔드 실행 실패: {e}")

    instance_id = uuid.uuid4().hex
    _instances[instance_id] = {"backend": backend, "frontend": frontend, "network": net}
    _active_by_problem[pid] = instance_id
    asyncio.create_task(_auto_cleanup(instance_id))

    return StartResponse(
        instance_id=instance_id,
        frontend_url=f"http://localhost:{f_port}",
        backend_port=b_port,
        frontend_port=f_port,
        network=net.name
    )

@router.post("/stop/{instance_id}", response_model=StopResponse)
def stop_problem(instance_id: str):
    if instance_id not in _instances:
        raise HTTPException(404, "인스턴스를 찾을 수 없습니다.")
    _cleanup(instance_id)
    return StopResponse(instance_id=instance_id, message="정상적으로 종료되었습니다.")

@router.post("/stop_by_problem/{problem_id}", response_model=StopResponse)
def stop_by_problem(problem_id: int):
    iid = _active_by_problem.get(problem_id)
    if not iid:
        raise HTTPException(404, "해당 문제 인스턴스가 없습니다.")
    _cleanup(iid)
    return StopResponse(instance_id=iid, message="정상적으로 종료되었습니다.")

@router.get("/instances")
def list_instances():
    return _active_by_problem
