from fastapi import FastAPI
import uvicorn

from splitwise.routers.auth import router as user_router

app = FastAPI(
    title="Splitwise", description="welcome to splitwise api clone", root_path="/api/v1"
)

app.include_router(router=user_router)
