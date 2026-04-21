from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime

from server.routes import auth, items, claims, admin, upload, cron
from server.database import supabase, update_claim, update_item, log_action

load_dotenv()

app = FastAPI(
    title="Spotter API",
    description="Centralized Campus Lost & Found Tracker",
    version="1.0.0"
)

# CORS — allow client to communicate with server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(claims.router, prefix="/api/claims", tags=["Claims"])
app.include_router(admin.router, prefix="/api/admin", tags=["Faculty Dashboard"])
app.include_router(upload.router, prefix="/api/upload", tags=["Uploads"])
app.include_router(cron.router, prefix="/api/cron", tags=["System Cron"])

# Only mount local static files if NOT running in Vercel.
# Vercel's edge network serves the static client folder natively via vercel.json.
if not os.environ.get("VERCEL"):
    app.mount("/uploads", StaticFiles(directory="server/uploads"), name="uploads")
    # Serve static client files locally
    app.mount("/", StaticFiles(directory="client", html=True), name="client")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Spotter API is running"}
