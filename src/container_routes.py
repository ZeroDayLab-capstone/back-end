import os
import asyncio
import socket
import random
import uuid

import docker
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Tuple

router = APIRouter()
client = docker.from_env()

# ── 문제별 이미지, 포트 범위, 플래그 정의 ─────────────────────────────────
PROBLEM_CONFIG: Dict[int, Dict[str, object]] = {
    1: {
        "frontend_image": "zeroday01478/csrf:frontend",
        "backend_image":  "zeroday01478/csrf:backend",
        "host_range":     (2000, 5000),
        "flag":           "FLAG{9c926de27b8995b218c8b1f51806ce21}",
    },
    2: {
        "frontend_image": "zeroday01478/sqli2:frontend",
        "backend_image":  "zeroday01478/sqli2:backend",
        "host_range":     (3000, 8000),
        "flag":           "<여기에 sqli2 플래그>",
    },
    3: {
        "frontend_image": "zeroday01478/sqli3:frontend",
        "backend_image":  "zeroday01478/sqli3:backend",
        "host_range":     (3000, 8000),
        "flag":           "<여기에 sqli3 플래그>",
    },
    4: {
        "frontend_image": "zeroday01478/command:frontend",
        "backend_image":  "zeroday01478/command:backend",
        "host_range":     (2000, 6000),
        "flag":           "<여기에 command 플래그>",
    },
    5: {
        "frontend_image": "zeroday01478/stored_xss_1:frontend",
        "backend_image":  "zeroday01478/stored_xss_1:backend",
        "host_range":     (2000, 6000),
        "flag":           "<여기에 stored_xss_1 플래그>",
    },
    6: {
        "frontend_image": "zeroday01478/stored_xss_2:frontend",
        "backend_image":  "zeroday01478/stored_xss_2:backend",
        "host_range":     (2000, 6000),
        "flag":           "<여기에 stored_xss_2 플래그>",
    },
    7: {
        "frontend_image": "zeroday01478/stored_xss_3:frontend",
        "backend_image":  "zeroday01478/stored_xss_3:backend",
        "host_range":     (2000, 6000),
        "flag":           "<여기에 stored_xss_3 플래그>",
    },
    8: {
        "frontend_image": "zeroday01478/reflected_xss:frontend",
        "backend_image":  "zeroday01478/reflected_xss:backend",
        "host_range":     (2000, 6000),
        "flag":           "<여기에 reflected_xss 플래그>",
    },
    9: {
        "frontend_image": "zeroday01478/file-upload:frontend",
        "backend_image":  "zeroday01478/file-upload:backend",
        "host_range":     (2000, 6000),
        "flag":           "<여기에 file-upload 플래그>",
    },
    10: {
        "frontend_image": "zeroday01478/path-traversal:frontend",
        "backend_image":  "zeroday01478/path-traversal:backend",
        "host_range":     (2000, 6000),
        "flag":           "<여기에 path-traversal 플래그>",
    },
    11: {
        "frontend_image": "zeroday01478/sqli:frontend",
        "backend_image":  "zeroday01478/sqli:backend",
        "host_range":     (3000, 8000),
        "flag":           "<여기에 sqli 플래그>",
    },
}

# ── 인스턴스 추적용 전역 변수 ───────────────────────────────────────────
_instances: Dict[str, dict]   = {}
_active_by_problem: Dict[int, str] = {}

# ── 요청/응답 모델 ─────────────────────────────────────────────────────
class StartRequest(BaseModel):
    problem_id: int

class StartResponse(BaseModel):
    instance_id: str
    backend_host: str
    backend_port: int
    frontend_host: str
    frontend_port: int
    network: str

class StopResponse(BaseModel):
    instance_id: str
    message: str

# ── 포트 할당 헬퍼 ──────────────────────────────────────────────────
def _find_free_port(port_range: Tuple[int, int]) -> int:
    start, end = port_range
    for _ in range(20):
        p = random.randint(start, end)
        with socket.socket() as s:
            try:
                s.bind(("0.0.0.0", p))
                return p
            except OSError:
                continue
    # 실패 시 OS에 맡김
    with socket.socket() as s:
        s.bind(("0.0.0.0", 0))
        return s.getsockname()[1]

# ── 컨테이너/네트워크 정리 ─────────────────────────────────────────
def _cleanup(instance_id: str):
    info = _instances.pop(instance_id, None)
    if not info:
        return
    # 백엔드, 프론트엔드 컨테이너 정리
    for role in ("backend", "frontend"):
        ctr = info.get(role)
        if ctr:
            try:
                ctr.stop(timeout=5)
                ctr.remove(force=True, v=True)
            except:
                pass
    # 네트워크 제거
    try:
        info["network"].remove()
    except:
        pass
    # _active_by_problem에서 삭제
    for pid, iid in list(_active_by_problem.items()):
        if iid == instance_id:
            _active_by_problem.pop(pid)

async def _auto_cleanup(instance_id: str, ttl_sec: int = 3600):
    await asyncio.sleep(ttl_sec)
    _cleanup(instance_id)

# ── Start API ───────────────────────────────────────────────────────
@router.post("/start", response_model=StartResponse)
async def start_containers(req: StartRequest):
    pid = req.problem_id
    cfg = PROBLEM_CONFIG.get(pid)
    if not cfg:
        raise HTTPException(status_code=400, detail="Invalid problem_id")

    # 이전에 남은 컨테이너/네트워크 삭제
    for ctr in client.containers.list(all=True):
        if ctr.name.startswith(f"prob_{pid}_"):
            try:
                ctr.remove(force=True, v=True)
            except:
                pass
    for net in client.networks.list():
        if net.name.startswith(f"prob_{pid}_"):
            try:
                net.remove()
            except:
                pass
    _active_by_problem.pop(pid, None)

    # 호스트 포트 할당
    backend_port = _find_free_port(cfg["host_range"])
    frontend_port = _find_free_port(cfg["host_range"])
    while frontend_port == backend_port:
        frontend_port = _find_free_port(cfg["host_range"])

    # 네트워크 생성
    net_name = f"prob_{pid}_{uuid.uuid4().hex[:8]}"
    try:
        network = client.networks.create(net_name, driver="bridge")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Network create failed: {e}")

    be_name = f"{net_name}_be"
    fe_name = f"{net_name}_fe"

    # ───────────────────── 경로 계산 ─────────────────────
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    UPLOADS_HOST_PATH = os.path.join(ROOT_DIR, "BE", "uploads")
    FLAG_PATH_FE = os.path.join(ROOT_DIR, "FE", "flag.txt")

    # FE 폴더 및 flag.txt 생성
    os.makedirs(os.path.dirname(FLAG_PATH_FE), exist_ok=True)
    try:
        with open(FLAG_PATH_FE, "w") as f:
            f.write(cfg["flag"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write FE flag.txt: {e}")

    # ───────────────────── 백엔드 컨테이너 실행 ─────────────────────
    try:
        backend = client.containers.run(
            image       = cfg["backend_image"],
            name        = be_name,
            detach      = True,
            network     = net_name,
            ports       = {"8000/tcp": backend_port},
            environment = {"FLAG": cfg["flag"]},
            volumes     = {
                UPLOADS_HOST_PATH: {"bind": "/app/uploads", "mode": "rw"}
            },
            remove      = False
        )
        try:
            network.disconnect(backend)
        except:
            pass
        network.connect(backend, aliases=["backend"])
    except Exception as e:
        try:
            network.remove()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Backend launch failed: {e}")

    # ───────────────────── 프론트엔드 컨테이너 실행 ─────────────────────
    try:
        if pid == 10:
            # Path-Traversal 문제: uploads + flag.txt 마운트
            env = {
                "BACKEND_URL": "http://backend:8000",
                "API_BASE":    "http://backend:8000",
            }
            volumes = {
                UPLOADS_HOST_PATH: {"bind": "/app/uploads", "mode": "rw"},
                FLAG_PATH_FE: {"bind": "/var/www/html/flag.txt", "mode": "ro"},
            }
        else:
            # 그 외 문제: flag.txt만 마운트
            env = {
                "API_URL":  "http://backend:8000",
                "API_BASE": "http://backend:8000",
            }
            volumes = {
                FLAG_PATH_FE: {"bind": "/var/www/html/flag.txt", "mode": "ro"},
            }

        frontend = client.containers.run(
            image       = cfg["frontend_image"],
            name        = fe_name,
            detach      = True,
            network     = net_name,
            ports       = {"80/tcp": frontend_port},
            environment = env,
            volumes     = volumes,
            remove      = False
        )
    except Exception as e:
        # 프론트엔드 실행 실패 시 뒤처리
        try:
            backend.stop(timeout=5)
            backend.remove(force=True, v=True)
            network.remove()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Frontend launch failed: {e}")

    # ───────────────────── 기록 및 자동 정리 스케줄링 ─────────────────────
    instance_id = uuid.uuid4().hex
    _instances[instance_id] = {
        "backend":  backend,
        "frontend": frontend,
        "network":  network,
    }
    _active_by_problem[pid] = instance_id
    asyncio.create_task(_auto_cleanup(instance_id))

    return StartResponse(
        instance_id   = instance_id,
        backend_host  = "100.108.98.2",  # 필요 시 localhost로 변경
        backend_port  = backend_port,
        frontend_host = "100.108.98.2",
        frontend_port = frontend_port,
        network       = net_name
    )

# ── Stop by instance ID API ────────────────────────────────────────────
@router.post("/stop/{instance_id}", response_model=StopResponse)
def stop_by_id(instance_id: str):
    if instance_id not in _instances:
        raise HTTPException(status_code=404, detail="Instance not found")
    _cleanup(instance_id)
    return StopResponse(instance_id=instance_id, message="Stopped and cleaned up")

# ── Stop by problem ID API ─────────────────────────────────────────────
@router.post("/stop_by_problem/{problem_id}", response_model=StopResponse)
def stop_by_problem(problem_id: int):
    iid = _active_by_problem.get(problem_id)
    if not iid:
        raise HTTPException(status_code=404, detail="No running instance for this problem")
    _cleanup(iid)
    return StopResponse(instance_id=iid, message="Stopped and cleaned up")

# ── List active instances ─────────────────────────────────────────────
@router.get("/instances")
def list_instances():
    """
    현재 실행 중인 문제 ID와 인스턴스 ID 매핑을 반환합니다.
    """
    return _active_by_problem
