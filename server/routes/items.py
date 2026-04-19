from fastapi import APIRouter, Depends, HTTPException
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import get_items, get_item, insert_item, update_item, delete_item, log_action
from models import ItemCreateRequest
from middleware import get_current_user, require_role

router = APIRouter()


@router.get("/")
async def list_items(
    type: str = None,
    status: str = None,
    category: str = None,
    search: str = None,
):
    """List all items — publicly readable with optional search/filter params."""
    items = get_items(type=type, status=status, category=category, search=search)
    return {"items": items}


@router.get("/{item_id}")
async def get_single_item(item_id: str):
    """Get a single item by ID."""
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/")
async def create_item(body: ItemCreateRequest, current_user: dict = Depends(get_current_user)):
    """Create a new lost or found report (authenticated users only)."""
    data = {
        "reporter_id": current_user["id"],
        "type": body.type,
        "title": body.title,
        "category": body.category,
        "description": body.description,
        "brand": body.brand,
        "color": body.color,
        "location_found": body.location_found,
        "status": "reported",
    }
    result = insert_item(data)
    log_action(
        actor_id=current_user["id"],
        action="CREATE_ITEM",
        target_type="item",
        target_id=result[0]["id"] if result else None,
        details={"title": body.title, "type": body.type},
    )
    return {"message": "Item reported successfully", "item": result}


@router.put("/{item_id}")
async def update_item_route(
    item_id: str,
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    """Update an item — owner or faculty only."""
    existing = get_item(item_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")

    is_owner = existing["reporter_id"] == current_user["id"]
    is_faculty = current_user["role"] == "faculty"

    if not is_owner and not is_faculty:
        raise HTTPException(status_code=403, detail="Permission denied")

    result = update_item(item_id, body)
    log_action(current_user["id"], "UPDATE_ITEM", "item", item_id, details=body)
    return {"message": "Item updated", "item": result}


@router.delete("/{item_id}")
async def delete_item_route(
    item_id: str,
    current_user: dict = Depends(require_role("faculty")),
):
    """Delete an item — faculty only."""
    existing = get_item(item_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")

    delete_item(item_id)
    log_action(current_user["id"], "DELETE_ITEM", "item", item_id)
    return {"message": "Item deleted"}
