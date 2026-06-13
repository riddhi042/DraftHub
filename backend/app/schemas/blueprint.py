from pydantic import BaseModel
 
 
class BlueprintCreate(BaseModel):
    name: str
    description: str | None = None
 
 
class RevisionCreate(BaseModel):
    notes: str | None = None
 