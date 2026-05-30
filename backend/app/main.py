from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api import config_api, courses, documents, knowledge_base, qa, questions, summaries
from app.core.settings import settings
from modules import db

db.init_db()

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RuntimeError)
async def runtime_error_handler(_: Request, exc: RuntimeError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok", "message": "COURSE_RAG_SYSTEM backend is running"}


app.include_router(courses.router, prefix=settings.api_prefix)
app.include_router(documents.router, prefix=settings.api_prefix)
app.include_router(knowledge_base.router, prefix=settings.api_prefix)
app.include_router(qa.router, prefix=settings.api_prefix)
app.include_router(questions.router, prefix=settings.api_prefix)
app.include_router(summaries.router, prefix=settings.api_prefix)
app.include_router(config_api.router, prefix=settings.api_prefix)
