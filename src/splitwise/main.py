from fastapi import FastAPI
import uvicorn

# from routers

app = FastAPI(
    title="Splitwise", description="welcome to splitwise api clone", root_path="/api/v1"
)

app.include_router()
