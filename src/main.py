from fastapi import FastAPI
from resources import labs_routes, mypage_routes  # 라우터 import
from resources import auth_routes, flag_routes
from resources import admin_routes
from database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from container_routes import router as container_router
from dotenv import load_dotenv
from resources import password_reset_routes
from resources import id_find_routes
from resources.qna_routes import router as qna_router  # ✅ QnA 라우터
import models  # ✅ 모델 인식용

Base.metadata.create_all(bind=engine)
app = FastAPI()

# 라우터 등록
app.include_router(mypage_routes.router, prefix="/mypage")     # 마이페이지 API
app.include_router(auth_routes.router, prefix="/auth")         # 로그인 API
app.include_router(labs_routes.router, prefix="/labs")         # 실습페이지 API
app.include_router(admin_routes.router, prefix="/admin")       # 관리자페이지 API
app.include_router(flag_routes.router, prefix="/flag")         # 플래그 제출 API
app.include_router(container_router, prefix="/containers")     
app.include_router(password_reset_routes.router, prefix="/auth")
app.include_router(id_find_routes.router)
app.include_router(qna_router, prefix="/qna")                  # ✅ QnA 라우터

# 🔥 CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 시 전체 허용, 배포 시 도메인 지정 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI root!"}
