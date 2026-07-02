from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemes import chunk_scheme
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):
    
    def __init__(self, db_client):
        super().__init__(db_client)
        
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
        
    
    async def create_chunk(self, chunk: chunk_scheme):
        
        data = chunk.model_dump(by_alias=True, exclude={"id"})
        
        result = await self.collection.insert_one(data)
        
        chunk.id = result.inserted_id
        
        return chunk
    
    async def get_chunk(self, chunk_id: str):
        
        # Return Dictionary
        result = await self.collection.find_one({
            "id": ObjectId(chunk_id)
        })
        
        if result is None:
            return None
        
        return chunk_scheme(**result)
    
    
    async def insert_many_chunks(self, chunks: list,batch_size: int = 100):
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i: i+batch_size]
            
            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]
            
            result = await self.collection.bulk_write(operations)
            
        return len(chunks)