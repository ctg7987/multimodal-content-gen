from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from typing import Dict, Any

from .schemas import GenerateRequest, JobStatusResponse
from .config import JOBS, CORS_ORIGINS
from .pipelines import text as text_pipeline
from .pipelines import promptify as promptify_pipeline
from .pipelines import image as image_pipeline
from .pipelines import score as score_pipeline
from .pipelines import rag as rag_pipeline


app = FastAPI(title="Multimodal Marketing Content Generator", version="0.1.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.post("/generate", response_model=JobStatusResponse)
def generate(payload: GenerateRequest) -> JobStatusResponse:
    job_id = str(uuid4())

    # Initialize job
    JOBS[job_id] = {
        "status": "processing",
        "progress": 0,
        "result": None,
        "input": payload.model_dump(),
    }

    # Enhanced multimodal pipeline execution
    try:
        # Retrieve brand context using RAG
        brand_context = rag_pipeline.rag_retrieve(payload.model_dump())
        
        # Generate enhanced prompts with brand context
        enhanced_payload = {**payload.model_dump(), "brand_context": brand_context}
        _prompt = promptify_pipeline.promptify(enhanced_payload)

        # Initialize multimodal results
        multimodal_copies = []
        images = []
        performance_predictions = []
        
        for ch in payload.channels:
            # Generate multimodal text content
            channel_data = {"channel": ch, **enhanced_payload}
            text_result = text_pipeline.generate_text(channel_data)
            
            # Generate images with enhanced context
            image_result = image_pipeline.generate_image(channel_data)
            
            # Store comprehensive results
            multimodal_copies.append({
                "channel": ch,
                "primary": text_result.get("primary", ""),
                "variations": text_result.get("variations", []),
                "engagement_score": text_result.get("engagement_score", 0.7),
                "optimization_tips": text_result.get("optimization_tips", [])
            })
            
            images.append(image_result)
            
            # Generate performance prediction
            performance_predictions.append({
                "channel": ch,
                "predicted_engagement": text_result.get("engagement_score", 0.7),
                "best_posting_time": get_optimal_posting_time(ch, payload.audience_target),
                "estimated_reach": calculate_estimated_reach(ch, text_result.get("engagement_score", 0.7))
            })

        # Score content with detailed metrics
        score_result = score_pipeline.score_content({
            "copies": [copy["primary"] for copy in multimodal_copies], 
            "images": images
        })

        # Complete with enhanced multimodal results
        result: Dict[str, Any] = {
            "multimodal_copies": multimodal_copies,
            "images": images,
            "performance_predictions": performance_predictions,
            "campaign_insights": generate_campaign_insights(multimodal_copies, performance_predictions),
            "meta": {
                "score": score_result,
                "brand_context": brand_context,
                "prompt_used": _prompt,
                "generation_settings": {
                    "content_length": payload.content_length,
                    "generate_variations": payload.generate_variations,
                    "include_emoji": payload.include_emoji
                }
            },
        }

        JOBS[job_id].update({
            "status": "completed",
            "progress": 100,
            "result": result,
        })

    except Exception as e:  # pragma: no cover - simple stub error path
        JOBS[job_id].update({
            "status": "failed",
            "progress": 100,
            "result": {"error": str(e)},
        })

    job = JOBS[job_id]
    return JobStatusResponse(job_id=job_id, status=job["status"], progress=job["progress"], result=job["result"])


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str) -> JobStatusResponse:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(job_id=job_id, status=job["status"], progress=job["progress"], result=job.get("result"))


def get_optimal_posting_time(channel: str, audience_target: dict) -> str:
    """Get optimal posting time based on channel and audience."""
    optimal_times = {
        "facebook": "1:00 PM - 3:00 PM",
        "instagram": "11:00 AM - 1:00 PM",
        "twitter": "12:00 PM - 3:00 PM",
        "email": "10:00 AM - 11:00 AM"
    }
    return optimal_times.get(channel, "12:00 PM - 2:00 PM")


def calculate_estimated_reach(channel: str, engagement_score: float) -> str:
    """Calculate estimated reach based on channel and engagement score."""
    base_reach = {
        "facebook": 1000,
        "instagram": 800,
        "twitter": 500,
        "email": 2000
    }
    
    estimated = base_reach.get(channel, 500) * engagement_score
    if estimated > 1000:
        return f"{estimated/1000:.1f}K"
    return str(int(estimated))


def generate_campaign_insights(multimodal_copies: list, performance_predictions: list) -> dict:
    """Generate overall campaign insights."""
    total_engagement = sum(pred["predicted_engagement"] for pred in performance_predictions)
    avg_engagement = total_engagement / len(performance_predictions) if performance_predictions else 0
    
    best_channel = max(performance_predictions, key=lambda x: x["predicted_engagement"]) if performance_predictions else None
    
    insights = {
        "overall_engagement_score": round(avg_engagement, 2),
        "best_performing_channel": best_channel["channel"] if best_channel else "None",
        "total_variations_generated": sum(len(copy["variations"]) for copy in multimodal_copies),
        "recommendations": []
    }
    
    # Add recommendations
    if avg_engagement > 0.8:
        insights["recommendations"].append("Excellent engagement potential - consider boosting budget")
    elif avg_engagement < 0.6:
        insights["recommendations"].append("Consider refining content strategy for better engagement")
    
    if best_channel and best_channel["predicted_engagement"] > avg_engagement + 0.1:
        insights["recommendations"].append(f"Focus budget on {best_channel['channel']} for best ROI")
    
    return insights


@app.get("/")
def root():
    return {"ok": True, "service": "multimodal-content-gen", "endpoints": ["/generate", "/jobs/{job_id}"]}
