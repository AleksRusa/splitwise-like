from fastapi import APIRouter, FastAPI
import uvicorn

from sqlalchemy.orm import configure_mappers
from splitwise.routers.auth import router as user_router
from splitwise.routers.group import router as group_router
from splitwise.routers.expense import router as expense_router

from splitwise.models import User, GroupMembers, Expense, ExpenseSplit, Group

configure_mappers()

app = FastAPI(
    title="Splitwise", description="welcome to splitwise api clone", root_path="/api/v1"
)

health_router = APIRouter(prefix="/health", tags=["health"])


@app.get("/check")
def health_check():
    return {"status": "ok"}


app.include_router(router=health_router)
app.include_router(router=user_router)
app.include_router(router=group_router)
app.include_router(router=expense_router)
