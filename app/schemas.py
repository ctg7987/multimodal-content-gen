from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class AudienceTarget(BaseModel):
    age_range: str = "25-45"
    gender: str = "all"
    location: str = "global"
    interests: List[str] = Field(default_factory=list)
    platform_preference: str = "all"


class BrandAssets(BaseModel):
    primary_color: str = "#10b981"
    secondary_color: str = "#059669"
    logo_url: Optional[str] = None
    brand_voice: str = "professional"  # professional, casual, humorous, friendly
    tone: str = "neutral"  # formal, neutral, casual
    brand_values: List[str] = Field(default_factory=lambda: ["quality", "innovation", "trust"])


class GenerateRequest(BaseModel):
    title: str
    brief: str
    brand_profile_id: str = Field(default="demo")
    channels: List[str] = Field(default_factory=list)
    audience_target: Optional[AudienceTarget] = None
    brand_assets: Optional[BrandAssets] = None
    generate_variations: bool = Field(default=True)
    content_length: str = Field(default="medium")  # short, medium, long
    include_emoji: bool = Field(default=False)


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    result: Optional[Dict[str, Any]] = None
