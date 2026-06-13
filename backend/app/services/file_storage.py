# backend/app/services/file_storage.py
"""
Handles saving uploaded files to local disk.
Files are stored under:  uploads/{project_id}/{blueprint_id}/{uuid}_{original_filename}
"""
 
import uuid
from pathlib import Path
 
from fastapi import UploadFile
 
from app.core.settings import get_settings
 
settings = get_settings()
 
 
def save_upload(
    file: UploadFile,
    project_id: int,
    blueprint_id: str,
) -> dict:
    """
    Saves an uploaded file to disk.
    Returns a dict with file metadata.
    """
    # Build directory path
    upload_dir = Path(settings.upload_dir) / str(project_id) / str(blueprint_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
 
    # Generate a unique stored filename to avoid collisions
    original_filename = file.filename or "unnamed"
    stored_filename = f"{uuid.uuid4().hex}_{original_filename}"
    file_path = upload_dir / stored_filename
 
    # Write file to disk
    contents = file.file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
 
    return {
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_path": str(file_path),
        "file_size_bytes": len(contents),
        "mime_type": file.content_type,
    }
 
 
def delete_file(file_path: str) -> None:
    """Deletes a file from disk if it exists."""
    path = Path(file_path)
    if path.exists():
        path.unlink()
