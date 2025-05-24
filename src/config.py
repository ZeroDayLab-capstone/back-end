# config.py
from typing import Dict, Tuple

# 실제 플래그 값
PROBLEM_FLAGS: Dict[int, str] = {
    1: "flag{csrf_attack_success}",
    2: "flag{sqli2_mastered}",
    3: "flag{sqli3_mastered}",
    4: "flag{command_injection_mastered}",
    5: "flag{stored_xss_1_mastered}",
    6: "flag{stored_xss_2_mastered}",
    7: "flag{stored_xss_3_mastered}",
    8: "flag{reflected_xss_mastered}",
    9: "flag{file_upload_mastered}",
   10: "flag{path_traversal_mastered}",
}

# frontend/backend 이미지 & 내부 포트 & 호스트 포트 범위
PROBLEM_CONFIGS: Dict[int, Dict[str, object]] = {
    1:  {"frontend_image":"zeroday01478/csrf:frontend",        "backend_image":"zeroday01478/csrf:backend",        "frontend_port":80,  "backend_port":8000, "host_range":(2000,5000)},
    2:  {"frontend_image":"zeroday01478/sqli2:frontend",      "backend_image":"zeroday01478/sqli2:backend",      "frontend_port":80,  "backend_port":8000, "host_range":(3000,8000)},
    3:  {"frontend_image":"zeroday01478/sqli3:frontend",      "backend_image":"zeroday01478/sqli3:backend",      "frontend_port":80,  "backend_port":8000, "host_range":(3000,8000)},
    4:  {"frontend_image":"zeroday01478/command:frontend",     "backend_image":"zeroday01478/command:backend",     "frontend_port":80,  "backend_port":8000, "host_range":(2000,6000)},
    5:  {"frontend_image":"zeroday01478/stored_xss_1:frontend","backend_image":"zeroday01478/stored_xss_1:backend","frontend_port":80,  "backend_port":8000, "host_range":(2000,6000)},
    6:  {"frontend_image":"zeroday01478/stored_xss_2:frontend","backend_image":"zeroday01478/stored_xss_2:backend","frontend_port":80,  "backend_port":8000, "host_range":(2000,6000)},
    7:  {"frontend_image":"zeroday01478/stored_xss_3:frontend","backend_image":"zeroday01478/stored_xss_3:backend","frontend_port":80,  "backend_port":8000, "host_range":(2000,6000)},
    8:  {"frontend_image":"zeroday01478/reflected_xss:frontend","backend_image":"zeroday01478/reflected_xss:backend","frontend_port":80, "backend_port":8000, "host_range":(2000,6000)},
    9:  {"frontend_image":"zeroday01478/file-upload:frontend", "backend_image":"zeroday01478/file-upload:backend", "frontend_port":80, "backend_port":8000, "host_range":(2000,6000)},
   10:  {"frontend_image":"zeroday01478/path-traversal:frontend","backend_image":"zeroday01478/path-traversal:backend","frontend_port":80,"backend_port":8000,"host_range":(2000,6000)},
}
