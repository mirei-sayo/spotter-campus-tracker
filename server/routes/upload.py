from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import supabase

router = APIRouter()

@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image type.")
    
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    
    try:
        # Read file bytes directly in memory (safe for Vercel)
        file_bytes = await file.read()
        
        # Upload to supabase 'uploads' bucket
        res = supabase.storage.from_("uploads").upload(
            path=unique_filename,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )
        
        # Get public url string
        public_url = supabase.storage.from_("uploads").get_public_url(unique_filename)
        return {"url": public_url}
        
    except Exception as e:
        print("Upload Error:", e)
        raise HTTPException(status_code=500, detail="Failed to upload image. Make sure the 'uploads' bucket is created and public.")
