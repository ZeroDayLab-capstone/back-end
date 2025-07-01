# WebSec Lab 백엔드

웹 보안 학습을 위한 실습(Lab) 플랫폼의 백엔드 API 서버입니다. 사용자 인증, 실습 진행, 설명 자료 제공 등의 기능을 제공합니다.

## 🛠️ 기술 스택

- **FastAPI**: 고성능 Python 웹 프레임워크 (비동기 지원)  
- **SQLAlchemy**: 데이터베이스 ORM 매핑 도구  
- **JWT (jose)**: 사용자 인증 및 권한 관리  
- **Pydantic**: 데이터 모델링 및 유효성 검증  
- **Passlib**: 비밀번호 해싱 및 검증  
- **python-dotenv**: `.env` 파일 기반 환경 변수 설정  
- **Docker**: 실습 환경 컨테이너화 및 자동 오케스트레이션  

---

## 📋 주요 기능

- 🔐 사용자 회원가입 및 로그인, JWT 기반 인증 처리  
- 🧪 실습 환경 접속, 실습 상태 관리 (`in-progress`, `completed`)  
- 📝 실습 문제 답안 제출 및 정오 판별  
- 📚 보안 주제별 해설 자료 제공  
- 🏁 플래그 제출 및 검증 기능  
- 🛠 관리자 기능 (사용자 목록, 실습 생성/수정, 로그, 서버 상태)  
- 🐳 실습 컨테이너 자동 생성/삭제 오케스트레이터 기능  



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

---

### 🔐 인증 API

- *POST* `/register` : 사용자 회원가입  
- *POST* `/login` : 사용자 로그인  
- *GET* `/me` : 현재 사용자 정보 조회 (JWT 인증 필요)
- *POST* `/find-id` : 이름과 휴대폰 번호로 아이디(이메일) 찾기
- *POST* `/password-reset/request` : 비밀번호 재설정 이메일 발송
- *POST* `/password-reset/confirm` : 비밀번호 재설정 완료



---

### 🧪 실습 API

- *POST* `/labs/environment` : 실습 환경 접속 및 진행 상태 기록 (`in-progress`)  
- *POST* `/labs/submit` : 실습 문제 답안 제출 및 정답 여부 판별  

---

### 🧑‍💻 마이페이지 API

- *GET* `/mypage/profile/{email}` : 사용자 프로필 조회  
- *PUT* `/mypage/profile/{email}` : 사용자 프로필 수정
- *PUT* `/mypage/profile/image` : 프로필 사진 업로드/수정 (multipart/form-data)
- *DELETE* `/mypage/profile/image` : 프로필 사진 삭제 (기본 이미지로 초기화) 
- *GET* `/mypage/ongoing-labs/{email}` : 진행 중인 실습 목록 조회  
- *GET* `/mypage/completed-labs/{email}` : 완료된 실습 목록 조회  

---

### 📚 해설 API

- *POST* `/resources/explanation` : 보안 주제별 설명 자료 조회  

---

### 🏁 플래그 API

- *POST* `/resources/submit_flag` : 플래그 정답 여부 확인  

---

### 🛠 관리자 API

- *GET* `/admin/users` : 전체 사용자 목록 조회  
- *POST* `/admin/labs` : 새 실습 문제 생성  
- *PUT* `/admin/labs/{lab_id}` : 실습 문제 수정  
- *GET* `/admin/user-results` : 사용자 실습 결과 조회  
- *GET* `/admin/logs` : 시스템 로그 조회  
- *GET* `/admin/server-status` : 서버 상태 확인  

---

### 🐳 실습 컨테이너 오케스트레이터

- *POST* `/start` : 문제 ID 기반 컨테이너 실행  
- *POST* `/stop/{instance_id}` : 인스턴스 ID 기준 컨테이너 중지  
- *POST* `/stop_by_problem/{problem_id}` : 문제 ID 기준 컨테이너 중지  
- *GET* `/instances` : 현재 실행 중인 컨테이너 목록 조회  

---

### 📝 Q&A 게시판 API

- *GET* `/qna/posts` : 전체 게시글 목록 조회
- *POST* `/qna/posts` : 게시글 작성 (로그인 필요)
- *GET* `/qna/posts/{post_id}` : 게시글 상세 및 댓글 조회
- *PUT* `/qna/posts/{post_id}` : 게시글 수정 (작성자/관리자)
- *DELETE* `/qna/posts/{post_id}` : 게시글 삭제 (작성자/관리자)
- *POST* `/qna/posts/{post_id}/comments` : 댓글 작성 (로그인 필요)
- *PUT* `/qna/comments/{comment_id}` : 댓글 수정 (작성자/관리자)
- *DELETE* `/qna/comments/{comment_id}` : 댓글 삭제 (작성자/관리자)

---

## 📝 주의사항
- 프로덕션 환경에서는 SECRET_KEY를 안전하게 관리하세요.
- 실제 배포 시 비밀번호 해싱 처리를 확인하세요(현재 mypage_routes.py에 비밀번호 평문 저장 이슈 있음).
- 배포 전 환경 변수와 보안 설정을 재검토하세요.
