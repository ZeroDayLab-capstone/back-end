import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Ensure FLAG is set for backend containers
env_flag = os.environ.get("FLAG")
if not env_flag:
    raise RuntimeError(
        "환경 변수 FLAG가 설정되지 않았습니다. Orchestrator 실행 시 반드시 FLAG 값을 설정하세요."
    )

import asyncio
import socket
import random
import uuid

import docker
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Tuple

router = APIRouter()
client = docker.from_env()

# Problem → Docker images & port ranges
PROBLEM_CONFIG: Dict[int, Dict[str, object]] = {
    1: {"frontend_image": "zeroday01478/csrf:frontend", "backend_image": "zeroday01478/csrf:backend", "host_range": (2000, 5000)},
    2: {"frontend_image": "zeroday01478/sqli2:frontend", "backend_image": "zeroday01478/sqli2:backend", "host_range": (3000, 8000)},
    3: {"frontend_image": "zeroday01478/sqli3:frontend", "backend_image": "zeroday01478/sqli3:backend", "host_range": (3000, 8000)},
    4: {"frontend_image": "zeroday01478/command:frontend", "backend_image": "zeroday01478/command:backend", "host_range": (2000, 6000)},
    5: {"frontend_image": "zeroday01478/stored_xss_1:frontend", "backend_image": "zeroday01478/stored_xss_1:backend", "host_range": (2000, 6000)},
    6: {"frontend_image": "zeroday01478/stored_xss_2:frontend", "backend_image": "zeroday01478/stored_xss_2:backend", "host_range": (2000, 6000)},
    7: {"frontend_image": "zeroday01478/stored_xss_3:frontend", "backend_image": "zeroday01478/stored_xss_3:backend", "host_range": (2000, 6000)},
    8: {"frontend_image": "zeroday01478/reflected_xss:frontend", "backend_image": "zeroday01478/reflected_xss:backend", "host_range": (2000, 6000)},
    9: {"frontend_image": "zeroday01478/file-upload:frontend", "backend_image": "zeroday01478/file-upload:backend", "host_range": (2000, 6000)},
   10: {"frontend_image": "zeroday01478/path-traversal:frontend", "backend_image": "zeroday01478/path-traversal:backend", "host_range": (2000, 6000)},
}

# In-memory tracking
_instances: Dict[str, dict] = {}
_active_by_problem: Dict[int, str] = {}

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
    with socket.socket() as s:
        s.bind(("0.0.0.0", 0))
        return s.getsockname()[1]


def _cleanup(instance_id: str):
    info = _instances.pop(instance_id, None)
    if not info:
        return
    for role in ("backend", "frontend"):
        ctr = info.get(role)
        if ctr:
            try:
                ctr.stop(timeout=5)
                ctr.remove(force=True, v=True)
            except Exception:
                pass
    try:
        info["network"].remove()
    except Exception:
        pass
    for pid, iid in list(_active_by_problem.items()):
        if iid == instance_id:
            _active_by_problem.pop(pid)


async def _auto_cleanup(instance_id: str, ttl_sec: int = 3600):
    await asyncio.sleep(ttl_sec)
    _cleanup(instance_id)


@router.post("/start", response_model=StartResponse)
async def start_containers(req: StartRequest):
    # Validate and cleanup old resources
    pid = req.problem_id
    cfg = PROBLEM_CONFIG.get(pid)
    if not cfg:
        raise HTTPException(400, detail="Invalid problem_id")

    # Remove leftover containers/networks for this problem
    for ctr in client.containers.list(all=True):
        if ctr.name.startswith(f"prob_{pid}_"):
            try:
                ctr.remove(force=True, v=True)
            except Exception:
                pass
    for net in client.networks.list():
        if net.name.startswith(f"prob_{pid}_"):
            try:
                net.remove()
            except Exception:
                pass
    _active_by_problem.pop(pid, None)

    # Allocate host ports
    brange = cfg["host_range"]
    backend_port = _find_free_port(brange)
    frontend_port = _find_free_port(brange)
    while frontend_port == backend_port:
        frontend_port = _find_free_port(brange)

    # Create isolated network
    net_name = f"prob_{pid}_{uuid.uuid4().hex[:8]}"
    try:
        network = client.networks.create(net_name, driver="bridge")
    except Exception as e:
        raise HTTPException(500, detail=f"Network create failed: {e}")

    be_name = f"{net_name}_be"
    fe_name = f"{net_name}_fe"

    # Launch backend container
    try:
        backend = client.containers.run(
            image=cfg["backend_image"],
            name=be_name,
            detach=True,
            network=net_name,
            ports={"8000/tcp": backend_port},
            environment={"FLAG": env_flag},
            remove=False
        )
        # Alias for internal DNS
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
        raise HTTPException(500, detail=f"Backend launch failed: {e}")

    # Launch frontend container
    try:
        frontend = client.containers.run(
            image=cfg["frontend_image"],
            name=fe_name,
            detach=True,
            network=net_name,
            ports={"80/tcp": frontend_port},
            environment={"API_URL": "http://backend:8000"},
            remove=False
        )
    except Exception as e:
        try:
            backend.stop(timeout=5)
            backend.remove(force=True, v=True)
            network.remove()
        except:
            pass
        raise HTTPException(500, detail=f"Frontend launch failed: {e}")

    # Track instance
    instance_id = uuid.uuid4().hex
    _instances[instance_id] = {"backend": backend, "frontend": frontend, "network": network}
    _active_by_problem[pid] = instance_id
    asyncio.create_task(_auto_cleanup(instance_id))

    return StartResponse(
        instance_id=instance_id,
        backend_host="localhost", backend_port=backend_port,
        frontend_host="localhost", frontend_port=frontend_port,
        network=net_name
    )


@router.post("/stop/{instance_id}", response_model=StopResponse)
def stop_by_id(instance_id: str):
    if instance_id not in _instances:
        raise HTTPException(404, detail="Instance not found")
    _cleanup(instance_id)
    return StopResponse(instance_id=instance_id, message="Stopped and cleaned up")


@router.post("/stop_by_problem/{problem_id}", response_model=StopResponse)
def stop_by_problem(problem_id: int):
    iid = _active_by_problem.get(problem_id)
    if not iid:
        raise HTTPException(404, detail="No running instance for this problem")
    _cleanup(iid)
    return StopResponse(instance_id=iid, message="Stopped and cleaned up")


@router.get("/instances")
def list_instances():
    return _active_by_problem
