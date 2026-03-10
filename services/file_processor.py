"""
services/file_processor.py — Extract text from uploaded files (PDF, DOCX, TXT, images).
"""

import os
import logging
import asyncio
from pathlib import Path
from typing import Optional
from config import UPLOAD_DIR, MAX_FILE_SIZE_MB, SUPPORTED_EXTENSIONS

log = logging.getLogger(__name__)
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_telegram_file(bot, file_id: str, original_name: str) -> Optional[str]:
    """Download a file from Telegram and save it locally."""
    try:
        tg_file = await bot.get_file(file_id)
        ext = Path(original_name).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return None
        safe_name = f"{file_id}{ext}"
        local_path = os.path.join(UPLOAD_DIR, safe_name)
        await tg_file.download_to_drive(local_path)
        return local_path
    except Exception as e:
        log.error("Failed to save Telegram file: %s", e)
        return None


def extract_text(file_path: str) -> str:
    """Extract text from a file based on its extension."""
    ext = Path(file_path).suffix.lower()
    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()[:8000]

        elif ext == ".pdf":
            try:
                import PyPDF2
                text = []
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages[:20]:
                        text.append(page.extract_text() or "")
                return "\n".join(text)[:8000]
            except Exception as e:
                log.error("PDF extraction failed: %s", e)
                return ""

        elif ext in (".docx", ".doc"):
            try:
                from docx import Document
                doc = Document(file_path)
                return "\n".join(p.text for p in doc.paragraphs if p.text.strip())[:8000]
            except Exception as e:
                log.error("DOCX extraction failed: %s", e)
                return ""

        elif ext in (".jpg", ".jpeg", ".png"):
            try:
                import pytesseract
                from PIL import Image
                img = Image.open(file_path)
                return pytesseract.image_to_string(img)[:4000]
            except Exception as e:
                log.warning("OCR failed (pytesseract may not be installed): %s", e)
                return ""

    except Exception as e:
        log.error("Text extraction error for %s: %s", file_path, e)
    return ""


def extract_keywords(text: str) -> str:
    """Simple keyword extraction — top words by frequency."""
    import re
    from collections import Counter
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                  "of", "with", "is", "are", "was", "were", "be", "been", "have", "has",
                  "do", "does", "did", "will", "would", "could", "should", "may", "might",
                  "el", "la", "los", "las", "un", "una", "de", "en", "y", "que", "es", "se"}
    words = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]{4,}\b', text.lower())
    filtered = [w for w in words if w not in stop_words]
    top = Counter(filtered).most_common(30)
    return ", ".join(w for w, _ in top)


