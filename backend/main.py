import os
import traceback
import logging
from dotenv import load_dotenv

load_dotenv()  # Load .env BEFORE importing services

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import analyze, training, cycle, users, escalation, wearable

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print(f"[DEBUG] CRUSOE_API_KEY loaded: {bool(os.getenv('CRUSOE_API_KEY'))}")
print(f"[DEBUG] PAID_API_KEY loaded: {bool(os.getenv('PAID_API_KEY'))}")
print(f"[DEBUG] QWEN_MODEL: {os.getenv('QWEN_MODEL')}")

app = FastAPI(
    title="PreHab API",
    description="Autonomous cycle-aware injury prevention agent",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lovable.dev", "https://*.lovable.dev", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    full_traceback = traceback.format_exc()
    logger.error("UNHANDLED EXCEPTION\nURL: %s\nMethod: %s\n%s",
                 request.url, request.method, full_traceback)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__}
    )

app.include_router(users.router,      prefix="/users",      tags=["users"])
app.include_router(training.router,   prefix="/training",   tags=["training"])
app.include_router(cycle.router,      prefix="/cycle",      tags=["cycle"])
app.include_router(analyze.router,    prefix="/analyse",    tags=["analyse"])
app.include_router(escalation.router, prefix="/escalation", tags=["escalation"])
app.include_router(wearable.router,   prefix="/wearable",   tags=["wearable"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "prehab-api"}