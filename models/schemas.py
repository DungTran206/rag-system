from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str
    file_filter: Optional[str] = None

class SourceChunk(BaseModel):
    chunk_id: str
    source_file: str
    page_number: Optional[int] = None
    similarity_score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk] = []

class IngestResponse(BaseModel):
    status: str
    filename: str
    total_chunks: int
    message: str