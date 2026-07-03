from pydantic import BaseModel, Field , field_validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime, timezone

class asset_scheme(BaseModel):
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: Optional[ObjectId] = Field(None,alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)
    
    # this will be the file_id which created after uploading file
    asset_name: str = Field(..., min_length=1)
    
    asset_size: int = Field(None, ge= 0)
    # When we added the file
    asset_pushed_at: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc))
    
    asset_config: dict = Field(default=None)
    
    
    @classmethod
    def get_indexes(cls):
        
        return [
            {
                "key": [
                    ("asset_project_id", 1)
                ],
                "name": "asset_project_id_index_1",
                "unique": False
            },
            {
                "key": [
                    ("asset_project_id", 1),
                    ("asset_name",1)
                ],
                "name": "asset_project_id_name_index_1",
                "unique": True
            }
        ]
    