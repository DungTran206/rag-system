from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import IngestResponse
from services.document_service import process_pdf_bytes
from services.vector_service import store_chunks_in_db, list_documents, delete_document_by_name, search_chunks
import traceback

router = APIRouter(prefix="/ingest", tags=["Data Ingestion"])

@router.post("/", response_model=IngestResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file định dạng PDF.")
    
    try:
        file_bytes = await file.read()
        
        chunks = process_pdf_bytes(file_bytes, file.filename)
        
        total_stored = store_chunks_in_db(chunks)
        
        return IngestResponse(
            status="success",
            filename=file.filename,
            total_chunks=total_stored,
            message="Đã nạp và lập chỉ mục dữ liệu thành công vào hệ thống RAG."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý file: {str(e)}")
    
@router.get("/files", response_model=list[str])
async def get_uploaded_files():
    """Lấy danh sách các file đang có trong Vector DB."""
    return list_documents()

@router.delete("/files/{filename:path}") 
async def delete_file(filename: str):
    try:
        current_files = list_documents()
        if filename not in current_files:
            raise HTTPException(status_code=404, detail="Không tìm thấy file này trên hệ thống.")
            
        delete_document_by_name(filename)
        return {"status": "success", "message": f"Đã xóa toàn bộ dữ liệu của file '{filename}'."}
        
    except HTTPException:
        raise
    except Exception as e:
        print("\n=== LỖI CHI TIẾT KHI XÓA FILE ===")
        traceback.print_exc()
        print("=================================\n")
        raise HTTPException(status_code=500, detail=str(e))