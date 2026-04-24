from pathlib import Path
from fastapi import HTTPException, UploadFile


# Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_file(file: UploadFile) -> None:
    """
    Validate uploaded file extension and size.
    
    Args:
        file: FastAPI UploadFile object
        
    Raises:
        HTTPException: If file is invalid (wrong type or too large)
    """
    # Validate extension
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {file_size / (1024*1024):.2f}MB. Maximum allowed: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )
