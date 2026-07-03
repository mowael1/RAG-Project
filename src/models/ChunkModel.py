from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemes import chunk_scheme
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):
    
    def __init__(self, db_client):
        super().__init__(db_client)
        
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
        

    #==========================================================#
    # indexing هنا بقي هنبدا اننا نضيف ال 

    # indexes الي هتضيف لينا ال function فاول حاجه احنا عملنا ال 
    # ده collection وهنبقي عاوزين اننا نستدعيها اول ما ننشا ال 
    async def init_collection(self):
        indexes = chunk_scheme.get_indexes()
        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )
            
    # ده collection دي بقي الي انت هتستعملها عشان تعمل ال 
    # فعملنا دي كحاجه وسيطه __init__ مينفعش اننا نضيفها جوه ال async function ودي عملناها لان ال 
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        
        return instance
    #==========================================================#
        
    
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
    
    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })
        
        return result.deleted_count