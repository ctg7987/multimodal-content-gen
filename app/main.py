from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from typing import Dict, Any

from .schemas import GenerateRequest, JobStatusResponse
from .config import JOBS
from .pipelines import text as text_pipeline
from .pipelines import promptify as promptify_pipeline
from .pipelines import image as image_pipeline
from .pipelines import score as score_pipeline
from .pipelines import rag as rag_pipeline


app = FastAPI(title="Multimodal Marketing Content Generator", version="0.1.0")

# Permissive CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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

    # Stubbed pipeline execution (synchronous and immediate for now)
    # TODO: Offload to background tasks or a queue system (e.g., Celery/RQ) when adding real providers
    try:
        # TODO: Use rag to retrieve knowledge
        _ctx = rag_pipeline.rag_retrieve(payload.model_dump())
        # TODO: prompt engineering
        _prompt = promptify_pipeline.promptify(payload.model_dump())

        copies = []
        images = []
        for ch in payload.channels:
            # TODO: call LLM provider
            copies.append(text_pipeline.generate_text({"channel": ch, **payload.model_dump()}))
            # TODO: call image provider (e.g., Replicate, SDXL)
            images.append(image_pipeline.generate_image({"channel": ch, **payload.model_dump()}))

        # TODO: score/critique content
        _score = score_pipeline.score_content({"copies": copies, "images": images})

        # Immediately complete with mocked results
        result: Dict[str, Any] = {
            "copy": copies,
            "images": images,
            "meta": {"score": _score},
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
