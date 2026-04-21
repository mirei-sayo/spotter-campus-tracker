from fastapi import APIRouter
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import supabase, update_claim, update_item, log_action
from datetime import datetime

router = APIRouter()

@router.get("/expire")
async def expire_reservations():
    """Triggered by Vercel Cron to expire claims."""
    now = datetime.utcnow().isoformat()
    res = supabase.table("claims").select("*").eq("status", "pending").lt("expires_at", now).execute()
    expired_count = 0
    if res and hasattr(res, 'data') and res.data:
        for claim in res.data:
            update_claim(claim["id"], {"status": "expired"})
            update_item(claim["item_id"], {"status": "found"})
            log_action("system", "EXPIRE_CLAIM", "claim", claim["id"], details={"item_id": claim["item_id"]})
            expired_count += 1
            
    return {"status": "success", "expired": expired_count}
