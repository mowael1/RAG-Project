from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import base
from helpers import get_settings

app = FastAPI()
settings = get_settings()


@asynccontextmanager
async def lifespan():
    
    print("Startup")
    yield
    print("shutdown")
    
    
app.include_router(base.base_router)