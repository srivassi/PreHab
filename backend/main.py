import os
from dotenv import load_dotenv

load_dotenv()  # Load .env BEFORE importing services

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analyze, training, cycle, users, escalation, wearable

print(f"[DEBUG] CRUSOE_API_KEY loaded: {bool(os.getenv('CRUSOE_API_KEY'))}")
print(f"[DEBUG] PAID_API_KEY loaded: {bool(os.getenv('PAID_API_KEY'))}")

app = FastAPI(
    title="PreHab API",
    description="Autonomous cycle-aware injury prevention agent",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
