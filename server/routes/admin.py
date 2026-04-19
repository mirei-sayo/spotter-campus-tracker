from fastapi import APIRouter, Depends, Query
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import get_items, get_claims, get_audit_log, supabase
from middleware import require_role

router = APIRouter()


@router.get("/stats")
async def dashboard_stats(current_user: dict = Depends(require_role("faculty"))):
    """Overview counts for the faculty dashboard."""
    all_items = supabase.table("items").select("status").execute().data
    all_claims = supabase.table("claims").select("status").execute().data

    stats = {
        "items": {
            "total": len(all_items),
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
    status: str = None,
    category: str = None,
    search: str = None,
    current_user: dict = Depends(require_role("faculty")),
):
    """Full item inventory with filters — faculty only."""
    items = get_items(status=status, category=category, search=search)
    return {"items": items}


@router.get("/claims")
async def all_claims(current_user: dict = Depends(require_role("faculty"))):
    """All pending claims for the faculty queue."""
    claims = get_claims()
    return {"claims": claims}
