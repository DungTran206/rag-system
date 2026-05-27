from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.ingest import router as ingest_router
from routers.query import router as query_router

app = FastAPI(
    title="My Full RAG API",
    description="Hệ thống RAG hoàn chỉnh với ChromaDB và FastAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online", 
        "message": "Chào mừng đến với RAG Backend API! Hệ thống đang chạy tốt."
    }

app.include_router(ingest_router)
app.include_router(query_router)