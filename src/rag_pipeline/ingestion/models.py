#we will check about the Data Validation
from pathlib import Path
from pydantic import BaseModel,Field

class Document(BaseModel):
    id:str
    text:str
    source_path:str
    source_name:str
    file_type:str
    metadata: dict = Field(default_factory=dict)