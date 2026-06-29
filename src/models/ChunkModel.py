from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemes import chunk_scheme

class ChunkModel(BaseDataModel):
    
    def __init__(self, db_client):
        super().__init__(db_client)
        
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
        
    
    async def create_chunk(self, chunk: chunk_scheme):
        
        data = chunk.model_dump(by_alias=True, exclude={"id"})
        
        result = await self.collection.insert_one(data)
        
        chunk.id = result.inserted_id
        
        return chunk
    
    async def get_chunk(self, chunk_id):