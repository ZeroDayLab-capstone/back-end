# docker_utils.py
import socket, random
from typing import Tuple

def find_free_port(port_range: Tuple[int,int]) -> int:
    """주어진 범위에서 사용 가능한 호스트 포트를 랜덤 검색"""
    start, end = port_range
    for _ in range(20):
        p = random.randint(start, end)
        with socket.socket() as s:
            try:
                s.bind(("0.0.0.0", p))
                return p
            except OSError:
                continue
    # fallback: OS가 할당한 포트
    with socket.socket() as s:
        s.bind(("0.0.0.0", 0))
        return s.getsockname()[1]
