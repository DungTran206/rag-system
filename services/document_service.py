import fitz  # PyMuPDF
import re

def clean_text(text: str) -> str:
    """Làm sạch khoảng trắng thừa và ký tự rác."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list:
    """Cắt text theo cơ chế cửa sổ trượt (Sliding Window)."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += (chunk_size - overlap)
        if end >= len(words):
            break
    return chunks

def process_pdf_bytes(file_bytes: bytes, filename: str) -> list:
    """Đọc file PDF trực tiếp từ RAM (không cần lưu ra ổ cứng), trả về danh sách chunk metadata."""
    doc = fitz.open("pdf", file_bytes)
    processed_chunks = []
    global_idx = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = clean_text(page.get_text())
        
        if not text:
            continue
            
        page_chunks = chunk_text(text)
        
        for chunk in page_chunks:
            processed_chunks.append({
                "chunk_id": f"{filename}_p{page_num+1}_{global_idx}",
                "text": chunk,
                "source": filename,
                "page_number": page_num + 1
            })
            global_idx += 1
            
    return processed_chunks