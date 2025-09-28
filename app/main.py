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

    # Enhanced pipeline execution with RAG and improved prompts
    try:
        # Retrieve brand context using RAG
        brand_context = rag_pipeline.rag_retrieve(payload.model_dump())
        
        # Generate enhanced prompts with brand context
        enhanced_payload = {**payload.model_dump(), "brand_context": brand_context}
        _prompt = promptify_pipeline.promptify(enhanced_payload)

        copies = []
        images = []
        for ch in payload.channels:
            # Generate text with enhanced context
            channel_data = {"channel": ch, **enhanced_payload}
            copies.append(text_pipeline.generate_text(channel_data))
            
            # Generate images with enhanced context
            images.append(image_pipeline.generate_image(channel_data))

        # Score content with detailed metrics
        score_result = score_pipeline.score_content({"copies": copies, "images": images})

        # Complete with enhanced results
        result: Dict[str, Any] = {
            "copy": copies,
            "images": images,
            "meta": {
                "score": score_result,
                "brand_context": brand_context,
                "prompt_used": _prompt
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


@app.get("/")
def root():
    return {"ok": True, "service": "multimodal-content-gen", "endpoints": ["/generate", "/jobs/{job_id}"]}
