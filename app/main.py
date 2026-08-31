# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import create_db_and_tables
from app.routers import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="ClauseIQ API",
    description="Contract & Policy Analyzer with Clause Intelligence",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth.router)


@app.get("/")
def health_check():
    return {"status": "ok", "app": "ClauseIQ"}