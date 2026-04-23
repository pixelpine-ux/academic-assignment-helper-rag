import io
from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text from uploaded file based on extension.
    
    Args:
        file_content: Raw file bytes
        filename: Original filename with extension
        
    Returns:
        Extracted text as string
        
    Raises:
        ValueError: If file type is unsupported or parsing fails
    """
    extension = Path(filename).suffix.lower()
    
    try:
        if extension == '.pdf':
            return _extract_from_pdf(file_content)
        elif extension == '.docx':
            return _extract_from_docx(file_content)
        elif extension == '.txt':
            return _extract_from_txt(file_content)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Failed to parse {extension} file: {str(e)}")


def _extract_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file."""
    pdf_file = io.BytesIO(file_content)
    reader = PdfReader(pdf_file)
    
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    
    if not text_parts:
        raise ValueError("PDF contains no extractable text")
    
    return "\n\n".join(text_parts)


def _extract_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file."""
    docx_file = io.BytesIO(file_content)
    doc = Document(docx_file)
    
    text_parts = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
    
    if not text_parts:
        raise ValueError("DOCX contains no text")
    
    return "\n\n".join(text_parts)


def _extract_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file."""
    try:
        return file_content.decode('utf-8')
    except UnicodeDecodeError:
        # Try with latin-1 as fallback
        return file_content.decode('latin-1')
