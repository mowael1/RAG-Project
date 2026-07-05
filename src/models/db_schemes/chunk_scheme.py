from pydantic import BaseModel, Field , field_validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId

class chunk_scheme(BaseModel):
    
    # This to make python deal with ObjectId
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: Optional[ObjectId] = Field(None,alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: object
    chunk_order: int = Field(..., gt=0)
    
    # This will tell me this chunk belong to any project
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId
    
    
        
    @classmethod
    def get_indexes(cls):
        
        return [
            {
                "key": [
                    ("chunk_project_id" , 1)
                ],
                "name": "chunk_project_id_index",
                "unique": False
            }
        ]