## Multimodal Marketing Content Generator

Minimal, runnable scaffold for a small FastAPI backend and Next.js (App Router) frontend that generates mocked marketing copy and placeholder images per channel. Structured for easy future swaps to providers like OpenAI/Replicate/CLIP.

### How it works

1) The web app submits a POST to `POST /generate` with `{ title, brief, brand_profile_id, channels[] }`.
2) The API creates a `job_id`, initializes an in-memory entry in `JOBS`, then synchronously runs stubbed pipelines.
3) The stubbed pipelines immediately return mocked results and mark the job `completed` with `progress=100` and a result:
	- `copy`: one entry per channel
	- `images`: placeholder URLs per channel (placehold.co)
4) The web app polls `GET /jobs/{job_id}` every second (max ~10 times) and renders status/progress; once completed it shows the results.

No external providers are called in this starter; TODOs mark where to plug in LLMs, image models, and RAG.

### Architecture at a glance

- FastAPI service with two endpoints: `/generate` and `/jobs/{id}`
- In-memory `JOBS` store (see `app/config.py`) for local development
- Pipeline stubs in `app/pipelines/*` to isolate provider integrations
- Next.js App Router UI in `web/app/*` with a simple form and polling loop
- Permissive CORS for local dev; switch to env-based origins later

### File tree

```
app/
	__init__.py
	main.py
	schemas.py
	config.py
	db.py
	pipelines/
		__init__.py
		text.py
		promptify.py
		image.py
		score.py
		rag.py
requirements.txt
web/
	package.json
	tsconfig.json
	next-env.d.ts
	app/
		layout.tsx
		page.tsx
.env.example
docker-compose.yml
.gitignore
README.md
```

### Quickstart

Backend

1) Install deps and run the API

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000 and submit the form.

Docker (API only)

```bash
docker compose up
```

### Example curl

```bash
curl -X POST http://127.0.0.1:8000/generate \
	-H "Content-Type: application/json" \
	-d '{"title":"Summer Sale","brief":"50% off all items","brand_profile_id":"123","channels":["email","instagram"]}'

curl http://127.0.0.1:8000/jobs/{job_id}
```

### Design notes

- In-memory JOBS dict for statuses/results; easy to swap to Redis/DB.
- Pipelines are simple stubs with TODOs for: RAG retrieval, prompt engineering, LLM copy generation, image generation, and scoring.
- CORS is permissive for local dev.
- No external API calls—everything is mocked.

### Troubleshooting

- If uvicorn cannot find the app, ensure you're in the repo root and use `uvicorn app.main:app --reload`.
- If the frontend can't reach the API, check CORS and that the API runs on port 8000.

### Next steps

- Plug in OpenAI/Replicate/CLIP in pipelines.
- Introduce .env-based config and secrets (see `.env.example`).
- Add Redis/DB job store and background workers.
- Add auth and env-based API URL for the web app.