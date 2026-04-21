from fastapi import APIRouter, Depends, Query
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import get_items, get_claims, get_audit_log, verify_item, log_action, supabase
from middleware import require_role

router = APIRouter()


@router.get("/stats")
async def dashboard_stats(current_user: dict = Depends(require_role("faculty"))):
    """Overview counts for the faculty dashboard."""
    all_items = supabase.table("items").select("status, is_verified").execute().data
    all_claims = supabase.table("claims").select("status").execute().data

    stats = {
        "items": {
            "total": len(all_items),
            "pending_verification": sum(1 for i in all_items if i.get("is_verified") == False),
            "reported": sum(1 for i in all_items if i["status"] == "reported"),
            "found": sum(1 for i in all_items if i["status"] == "found"),
            "reserved": sum(1 for i in all_items if i["status"] == "reserved"),
            "claimed": sum(1 for i in all_items if i["status"] == "claimed"),
            "closed": sum(1 for i in all_items if i["status"] == "closed"),
        },
        "claims": {
            "total": len(all_claims),
            "pending": sum(1 for c in all_claims if c["status"] == "pending"),
            "approved": sum(1 for c in all_claims if c["status"] == "approved"),
            "rejected": sum(1 for c in all_claims if c["status"] == "rejected"),
        },
    }
    return stats


@router.get("/audit-log")
async def audit_log(
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=100),
    current_user: dict = Depends(require_role("faculty")),
):
    """Paginated, read-only audit log for faculty."""
    logs = get_audit_log(page=page, limit=limit)
    return {"page": page, "limit": limit, "logs": logs}


@router.get("/inventory")
async def inventory(
    type: str = None,
    status: str = None,
    category: str = None,
    search: str = None,
    current_user: dict = Depends(require_role("faculty")),
):
    """Full item inventory with filters — faculty only."""
    items = get_items(type=type, status=status, category=category, search=search, all_items=True)
    return {"items": items}

@router.get("/unverified")
async def unverified_inventory(current_user: dict = Depends(require_role("faculty"))):
    """Get all unverified items."""
    res = supabase.table("items").select("*, profiles(full_name, email)").eq("is_verified", False).order("created_at", desc=True).execute()
    return {"items": res.data}

@router.put("/verify/{item_id}")
async def approve_item(item_id: str, current_user: dict = Depends(require_role("faculty"))):
    """Admin approves an unverified item."""
    verify_item(item_id)
    log_action(current_user["id"], "VERIFY_ITEM", "item", item_id)
    return {"message": "Item verified successfully."}


@router.get("/claims")
async def all_claims(current_user: dict = Depends(require_role("faculty"))):
    """All pending claims for the faculty queue."""
    claims = get_claims()
    return {"claims": claims}
