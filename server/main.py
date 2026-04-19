from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

from routes import auth, items, claims, admin

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

# Serve static client files
app.mount("/", StaticFiles(directory="client", html=True), name="client")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Spotter API is running"}
