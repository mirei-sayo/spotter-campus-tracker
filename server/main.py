from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime

from server.routes import auth, items, claims, admin, upload
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

app.mount("/uploads", StaticFiles(directory="server/uploads"), name="uploads")
# Serve static client files
app.mount("/", StaticFiles(directory="client", html=True), name="client")


async def expire_reservations_task():
    while True:
        try:
            now = datetime.utcnow().isoformat()
            res = supabase.table("claims").select("*").eq("status", "pending").lt("expires_at", now).execute()
            if res and hasattr(res, 'data') and res.data:
                for claim in res.data:
                    update_claim(claim["id"], {"status": "expired"})
                    update_item(claim["item_id"], {"status": "found"})
                    log_action("system", "EXPIRE_CLAIM", "claim", claim["id"], details={"item_id": claim["item_id"]})
        except Exception as e:
            pass
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(expire_reservations_task())

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Spotter API is running"}
