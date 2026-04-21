from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import uuid

router = APIRouter()
UPLOAD_DIR = "server/uploads"

@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image type.")
    
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": f"/uploads/{unique_filename}"}
