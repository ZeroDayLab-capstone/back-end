from fastapi import FastAPI
from database import Base, engine
from resource.auth_routes import router as auth_router
from resource.mypage_routes import router as mypage_router
from resource.main_routes import router as main_router
from resource.labs_routes import router as labs_router
from resource.explanation_routes import router as explanation_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router,prefix="/auth")
app.include_router(mypage_router,prefix="/mypage")
app.include_router(main_router,prefix="/main")
app.include_router(labs_router,prefix="/labs")
app.include_router(explanation_router,prefix="/explanation")


@app.get("/")
def read_root():
    return {"Hello": "World"}
#poetry run uvicorn main:app --reloads