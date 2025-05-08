# WebSec Lab 백엔드

웹 보안 학습을 위한 실습(Lab) 플랫폼의 백엔드 API 서버입니다. 사용자 인증, 실습 진행, 설명 자료 제공 등의 기능을 제공합니다.

## 🛠️ 기술 스택

- **FastAPI**: 고성능 API 프레임워크
- **SQLAlchemy**: ORM
- **JWT**: 사용자 인증 처리
- **Pydantic**: 데이터 검증
- **Passlib**: 비밀번호 해싱
- **Python-dotenv**: 환경 변수 관리

## 📋 주요 기능

- 사용자 회원가입 및 로그인
- 실습 환경 및 힌트 제공
- 실습 문제 제출 및 결과 확인
- 보안 주제 설명 자료 제공
- 관리자 기능 (사용자 관리, 로그 조회 등)

## 🔧 설치 및 설정

1. 저장소 클론
   ```bash
   git clone <repository-url>
   cd back-end
   ```

2. 가상 환경 설정
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    # .venv\Scripts\activate   # Windows
    ```

3. 의존성 설치
    ```bash
    pip install -r requirements.txt
    ```

4. 환경 변수 설정 .env 파일 생성:
    ```bash
    SECRET_KEY=test
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

## 🚀 실행 방법
다음 명령어로 개발 서버를 실행합니다:
```bash
cd BE  # BE 디렉토리로 이동
uvicorn main:app --reload
```

서버는 기본적으로 http://127.0.0.1:8000 에서 실행됩니다.

## 📚 API 문서
서버 실행 후 다음 URL에서 Swagger UI 문서를 확인할 수 있습니다:
- http://127.0.0.1:8000/docs

## 🗂️ 프로젝트 구조
```
BE/
├── database.py         # 데이터베이스 설정
├── main.py             # 애플리케이션 시작점
├── models.py           # 데이터베이스 모델
├── schemas.py          # 스키마 정의
├── websec.db           # SQLite 데이터베이스
└── resources/          # API 라우트 모듈
    ├── admin_routes.py     # 관리자 기능
    ├── auth_routes.py      # 인증 관련 API
    ├── explanation_routes.py # 설명 자료 API
    ├── labs_routes.py      # 실습 관련 API
    ├── main_routes.py      # 메인 페이지 API
    └── mypage_routes.py    # 마이페이지 API
```

## ✅ API 엔드포인트
인증 API
- POST /auth/register: 사용자 회원가입
- POST /auth/login: 사용자 로그인

실습 API
- GET /labs/environment: 실습 환경 접속 URL
- POST /labs/submit: 실습 문제 답안 제출
- GET /labs/hint/{lab_id}: 실습 힌트 조회
- GET /labs/feedback/{lab_id}: 실습 피드백 조회

마이페이지 API
- GET /mypage/ongoing-labs/{user_id}: 진행 중인 실습 조회
- GET /mypage/completed-labs/{user_id}: 완료된 실습 조회
- PUT /mypage/profile/{user_id}: 사용자 프로필 수정

설명 자료 API
- POST /explanation/explanation: 보안 주제 설명 자료 조회

관리자 API
- GET /admin/users: 전체 사용자 목록
- POST /admin/labs: 새 실습 생성
- GET /admin/user-results: 사용자 실습 결과 조회
- GET /admin/logs: 시스템 로그 조회

## 📝 주의사항
- 프로덕션 환경에서는 SECRET_KEY를 안전하게 관리하세요.
- 실제 배포 시 비밀번호 해싱 처리를 확인하세요(현재 mypage_routes.py에 비밀번호 평문 저장 이슈 있음).
- 배포 전 환경 변수와 보안 설정을 재검토하세요.