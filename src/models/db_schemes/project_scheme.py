from pydantic import BaseModel, Field , field_validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId

class project_scheme(BaseModel):
    
    # This to make python deal with ObjectId
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: Optional[ObjectId] = Field(None,alias="_id")
    project_id: str =  Field(...,min_length=1)
    
    # Make validation on project_id to make sure that it's only characters or numbers
    @field_validator("project_id")
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric")
        return value
    