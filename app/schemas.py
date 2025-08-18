from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    title: str
    brief: str
    brand_profile_id: str = Field(default="demo")
    channels: List[str] = Field(default_factory=list)


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    result: Optional[Dict[str, Any]] = None
