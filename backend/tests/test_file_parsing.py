import pytest
from pathlib import Path
from app.services.file_parser_service import extract_text_from_file
from app.core.file_validator import validate_file, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from fastapi import HTTPException, UploadFile
from io import BytesIO


class MockUploadFile:
    """Mock UploadFile for testing"""
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.file = BytesIO(content)
        self.content_type = "application/octet-stream"


def test_extract_text_from_txt():
    """Test TXT file parsing"""
    content = b"This is a test document.\n\nIt has multiple lines."
    text = extract_text_from_file(content, "test.txt")
    assert "This is a test document" in text
    assert "multiple lines" in text


def test_extract_text_unsupported_type():
    """Test unsupported file type raises error"""
    content = b"fake content"
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text_from_file(content, "test.exe")


def test_validate_file_valid_extension():
    """Test valid file extensions pass validation"""
    for ext in ['.txt', '.pdf', '.docx']:
        file = MockUploadFile(f"test{ext}", b"content")
        validate_file(file)  # Should not raise


def test_validate_file_invalid_extension():
    """Test invalid file extension raises HTTPException"""
    file = MockUploadFile("test.exe", b"content")
    with pytest.raises(HTTPException) as exc:
        validate_file(file)
    assert exc.value.status_code == 400
    assert "Unsupported file type" in exc.value.detail


def test_validate_file_too_large():
    """Test oversized file raises HTTPException"""
    large_content = b"x" * (MAX_FILE_SIZE + 1)
    file = MockUploadFile("test.txt", large_content)
    with pytest.raises(HTTPException) as exc:
        validate_file(file)
    assert exc.value.status_code == 400
    assert "File too large" in exc.value.detail


def test_validate_file_empty():
    """Test empty file raises HTTPException"""
    file = MockUploadFile("test.txt", b"")
    with pytest.raises(HTTPException) as exc:
        validate_file(file)
    assert exc.value.status_code == 400
    assert "File is empty" in exc.value.detail


def test_allowed_extensions():
    """Test that allowed extensions are correctly defined"""
    assert '.txt' in ALLOWED_EXTENSIONS
    assert '.pdf' in ALLOWED_EXTENSIONS
    assert '.docx' in ALLOWED_EXTENSIONS
    assert len(ALLOWED_EXTENSIONS) == 3
