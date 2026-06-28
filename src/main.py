from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import base, data
from helpers import get_settings
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()
settings = get_settings()


@asynccontextmanager
async def lifespan():
    
    # Here we make connection one Mongodb
    app.mongo_connection = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Here we connect on mini-rag database (where we save the data)
    app.mongo_db = app.mongo_connection[settings.MONGODB_DATABASE_NAME]
    
    yield
    
    # Here we close the connection
    app.mongo_connection.close()
    
    
app.include_router(base.base_router)
app.include_router(data.data_router)