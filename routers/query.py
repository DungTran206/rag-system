from fastapi import APIRouter, HTTPException
from models.schemas import QueryRequest, QueryResponse, SourceChunk
from services.vector_service import search_chunks
from services.llm_service import generate_rag_answer

router = APIRouter(prefix="/query", tags=["RAG Generation"])

@router.post("/", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    try:
        relevant_chunks = search_chunks(
            request.question, 
            top_k=3, 
            threshold=0.30, 
            file_filter=request.file_filter
        )
        
        answer = generate_rag_answer(request.question, relevant_chunks)
        
        sources = [
            SourceChunk(
                chunk_id=c["chunk_id"],
                source_file=c["source"],
                page_number=c["page_number"],
                similarity_score=c["similarity_score"]
            ) for c in relevant_chunks
        ]
        
        return QueryResponse(answer=answer, sources=sources)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")