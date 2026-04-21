from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in your .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ─────────────────────────────────────────
#  Profile Helpers
# ─────────────────────────────────────────

def get_profile(user_id: str):
    """Fetch a user profile by ID."""
    res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    return res.data


def create_profile(user_id: str, email: str, full_name: str, role: str, student_id: str = None, department: str = None):
    """Insert a new profile row after Supabase Auth signup."""
    data = {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "role": role,
        "student_id": student_id,
        "department": department,
    }
    res = supabase.table("profiles").insert(data).execute()
    return res.data


# ─────────────────────────────────────────
#  Item Helpers
# ─────────────────────────────────────────

def get_items(type: str = None, status: str = None, category: str = None, search: str = None, reporter_id: str = None, all_items: bool = False):
    """Fetch items with optional filters."""
    query = supabase.table("items").select("*, profiles(full_name, email)")
    
    if not all_items:
        if reporter_id:
            query = query.or_(f"is_verified.eq.true,reporter_id.eq.{reporter_id}")
        else:
            query = query.eq("is_verified", True)

    if type:
        query = query.eq("type", type)
    if status:
        query = query.eq("status", status)
    if category:
        query = query.eq("category", category)
    if search:
        query = query.ilike("title", f"%{search}%")
    res = query.order("created_at", desc=True).execute()
    return res.data


def get_item(item_id: str):
    """Fetch a single item by ID."""
    res = supabase.table("items").select("*, profiles(full_name, email)").eq("id", item_id).single().execute()
    return res.data


def insert_item(data: dict):
    """Insert a new item report."""
    res = supabase.table("items").insert(data).execute()
    return res.data


def update_item(item_id: str, data: dict):
    """Update an existing item."""
    res = supabase.table("items").update(data).eq("id", item_id).execute()
    return res.data

def verify_item(item_id: str):
    """Mark an item as verified."""
    res = supabase.table("items").update({"is_verified": True}).eq("id", item_id).execute()
    return res.data


def delete_item(item_id: str):
    """Delete an item (faculty only)."""
    res = supabase.table("items").delete().eq("id", item_id).execute()
    return res.data


# ─────────────────────────────────────────
#  Claim Helpers
# ─────────────────────────────────────────

def get_claims(claimant_id: str = None, item_id: str = None):
    """Fetch claims — all (faculty) or filtered by user."""
    query = supabase.table("claims").select("*, items(title, category), profiles!claims_claimant_id_fkey(full_name)")
    if claimant_id:
        query = query.eq("claimant_id", claimant_id)
    if item_id:
        query = query.eq("item_id", item_id)
    res = query.order("reserved_at", desc=True).execute()
    return res.data


def insert_claim(data: dict):
    """Create a new claim/reservation."""
    res = supabase.table("claims").insert(data).execute()
    return res.data


def update_claim(claim_id: str, data: dict):
    """Update a claim status."""
    res = supabase.table("claims").update(data).eq("id", claim_id).execute()
    return res.data


# ─────────────────────────────────────────
#  Audit Log Helpers
# ─────────────────────────────────────────

def log_action(actor_id: str, action: str, target_type: str, target_id: str = None, details: dict = None):
    """Insert an audit log entry."""
    data = {
        "actor_id": actor_id,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "details": details or {},
    }
    res = supabase.table("audit_log").insert(data).execute()
    return res.data


def get_audit_log(page: int = 1, limit: int = 50):
    """Fetch paginated audit log entries."""
    offset = (page - 1) * limit
    res = (
        supabase.table("audit_log")
        .select("*, profiles(full_name, role)")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return res.data
