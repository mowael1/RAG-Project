from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import base, data
from helpers import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from stores.llm import LLMProviderFactory

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # Here we make connection on Mongodb
    app.mongo_connection = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Here we connect on mini-rag database (where we save the data)
    app.mongo_db_client = app.mongo_connection[settings.MONGODB_DATABASE_NAME]
    
    # Provider Factory
    llm_provider_factory = LLMProviderFactory(settings)
    
    # Set Generation Model
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)
    
    # Set Embedding Model
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id= settings.EMBEDDING_MODEL_ID, 
                                            embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    yield
    
    # Here we close the connection
    app.mongo_connection.close()


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)