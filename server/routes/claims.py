from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import get_claims, insert_claim, update_claim, update_item, get_item, log_action
from models import ClaimCreateRequest
from middleware import get_current_user, require_role

router = APIRouter()

RESERVATION_HOURS = 48


@router.post("/")
async def create_claim(body: ClaimCreateRequest, current_user: dict = Depends(get_current_user)):
    """Student reserves a found item — 48-hour window starts now."""
    if current_user["role"] not in ("student",):
        raise HTTPException(status_code=403, detail="Only students can claim items.")

    item = get_item(body.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item["status"] not in ("reported", "found"):
        raise HTTPException(status_code=400, detail=f"Item is already {item['status']} and cannot be claimed.")

    now = datetime.utcnow()
    data = {
        "item_id": body.item_id,
        "claimant_id": current_user["id"],
        "status": "pending",
        "proof_description": body.proof_description,
        "proof_image_url": body.proof_image_url,
        "reserved_at": now.isoformat(),
        "expires_at": (now + timedelta(hours=RESERVATION_HOURS)).isoformat(),
    }
    claim = insert_claim(data)

    # Mark item as reserved
    update_item(body.item_id, {"status": "reserved"})
    log_action(current_user["id"], "CREATE_CLAIM", "claim", claim[0]["id"] if claim else None)

    return {"message": "Item reserved for 48 hours. Await faculty approval.", "claim": claim}


@router.get("/")
async def list_claims(current_user: dict = Depends(get_current_user)):
    """Faculty sees all claims; students see only their own."""
    if current_user["role"] == "faculty":
        claims = get_claims()
    else:
        claims = get_claims(claimant_id=current_user["id"])
    return {"claims": claims}


@router.put("/{claim_id}/approve")
async def approve_claim(
    claim_id: str,
    current_user: dict = Depends(require_role("faculty")),
):
    """Faculty approves a claim — marks item as claimed."""
    now = datetime.utcnow()
    result = update_claim(claim_id, {
        "status": "approved",
        "resolved_by": current_user["id"],
        "resolved_at": now.isoformat(),
    })
    if result:
        update_item(result[0]["item_id"], {"status": "claimed"})
    log_action(current_user["id"], "APPROVE_CLAIM", "claim", claim_id)
    return {"message": "Claim approved. Item marked as claimed."}


@router.put("/{claim_id}/reject")
async def reject_claim(
    claim_id: str,
    current_user: dict = Depends(require_role("faculty")),
):
    """Faculty rejects a claim — item returns to catalog."""
    now = datetime.utcnow()
    result = update_claim(claim_id, {
        "status": "rejected",
        "resolved_by": current_user["id"],
        "resolved_at": now.isoformat(),
    })
    if result:
        update_item(result[0]["item_id"], {"status": "found"})
    log_action(current_user["id"], "REJECT_CLAIM", "claim", claim_id)
    return {"message": "Claim rejected. Item returned to catalog."}


@router.put("/{claim_id}/close")
async def close_claim(
    claim_id: str,
    current_user: dict = Depends(require_role("faculty")),
):
    """Faculty closes/archives a resolved claim — item marked as closed."""
    now = datetime.utcnow()
    result = update_claim(claim_id, {
        "status": "closed",
    })
    if result:
        update_item(result[0]["item_id"], {"status": "closed"})
    log_action(current_user["id"], "CLOSE_CLAIM", "claim", claim_id)
    return {"message": "Claim closed and item archived."}
