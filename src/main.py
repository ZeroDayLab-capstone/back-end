from fastapi import FastAPI
from resources import labs_routes, main_routes, mypage_routes  # 라우터 import
from resources import auth_routes, explanation_routes, flag_routes
from resources import admin_routes
from database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from container_operations import router as container_router

Base.metadata.create_all(bind=engine)
app = FastAPI()

# 라우터 등록
app.include_router(main_routes.router, prefix="/main")     # 메인 페이지 API
app.include_router(mypage_routes.router, prefix="/mypage") # 마이페이지 API
app.include_router(auth_routes.router, prefix="/auth")     # 로그인 API
app.include_router(explanation_routes.router, prefix="/subject") # 해설 페이지 API
app.include_router(labs_routes.router, prefix="/labs")     # 실습페이지 API
app.include_router(admin_routes.router, prefix="/admin")   # 관리자페이지 API
app.include_router(flag_routes.router, prefix="/flag")     # 플래그 제출 API
app.include_router(container_router, prefix="/containers")

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