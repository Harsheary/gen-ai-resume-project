from pydantic import Field
from typing import TypedDict, Optional, List, Dict, Any
from pymongo.asynchronous.collection import AsyncCollection
from ..db import database


class FileSchema(TypedDict):
    name: str = Field(..., description="Name of the file")
    status: str = Field(..., description="Status of the file")
    job_description: Optional[str] = Field(None, description="Original job description")
    enhanced_job_description: Optional[str] = Field(None, description="Enhanced job description")
    result: Optional[str] = Field(None, description="Result of the ai call")
    analysis: Optional[Dict[str, Any]] = Field(None, description="Structured analysis results")


COLLECTION_NAME = "files"
files_collection: AsyncCollection = database[COLLECTION_NAME]