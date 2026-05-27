import chromadb
from sentence_transformers import SentenceTransformer

print("Đang tải mô hình Embedding & Khởi động ChromaDB...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="./data/chroma_storage")

collection = chroma_client.get_or_create_collection(
    name="rag_documents", 
    metadata={"hnsw:space": "cosine"}
)

def store_chunks_in_db(chunks: list):
    """Mã hóa danh sách chunk thành vector và lưu vào ChromaDB."""
    if not chunks:
        return 0

    ids = [item["chunk_id"] for item in chunks]
    documents = [item["text"] for item in chunks]
    metadatas = [{"source": item["source"], "page_number": item["page_number"]} for item in chunks]
    
    embeddings = embedding_model.encode(documents).tolist()
    
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    
    return len(ids)

def list_documents() -> list:
    """Lấy danh sách tất cả các tên file độc nhất đã được nạp vào DB."""
    results = collection.get(include=['metadatas'])
    metadatas = results.get('metadatas', [])
    unique_files = list(set([meta['source'] for meta in metadatas if meta]))
    return unique_files

def delete_document_by_name(filename: str):
    """Xóa hoàn toàn một file bằng cách lấy danh sách ID và xóa theo từng lô."""
    results = collection.get(where={"source": filename})
    ids_to_delete = results.get("ids", [])
    
    if not ids_to_delete:
        print(f"Không tìm thấy dữ liệu nào của file {filename} để xóa.")
        return
    
    DELETE_BATCH_SIZE = 100
    for i in range(0, len(ids_to_delete), DELETE_BATCH_SIZE):
        batch_ids = ids_to_delete[i : i + DELETE_BATCH_SIZE]
        collection.delete(ids=batch_ids)
        
    print(f"Đã xóa thành công tổng cộng {len(ids_to_delete)} chunks của file '{filename}'")

def search_chunks(query_text: str, top_k: int = 3, threshold: float = 0.25, file_filter: str = None) -> list:
    """Tìm kiếm các chunk tương đồng, có tích hợp LOG DEBUG để kiểm tra lỗi."""
    query_vector = embedding_model.encode(query_text).tolist()
    
    where_clause = {"source": file_filter} if file_filter else None
    
    print(f"\n🎯 [DEBUG TRUY VẤN]")
    print(f" ├─ Câu hỏi: {query_text}")
    print(f" └─ Bộ lọc file đang dùng: {where_clause}")

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        where=where_clause
    )
    
    matched_chunks = []
    if not results['ids'] or not results['ids'][0]: 
        print(" ❌ Kết quả: ChromaDB trả về RỖNG hoàn toàn (Không tìm thấy gì)!")
        return matched_chunks

    print(f" 📄 Tìm thấy {len(results['ids'][0])} mẩu tin thô. Kiểm tra điểm số (Threshold tối thiểu: {threshold}):")
    
    for idx in range(len(results['ids'][0])):
        distance = results['distances'][0][idx]
        similarity_score = 1.0 - distance
        filename = results['metadatas'][0][idx]['source']
        
        print(f"   ├─ Mẩu {idx+1} thuộc file: [{filename}]")
        print(f"   └─ Điểm tương đồng thực tế: {similarity_score:.4f} -> {'✅ ĐẠT' if similarity_score >= threshold else '❌ BỊ LOẠI'}")
        
        if similarity_score >= threshold:
            matched_chunks.append({
                "chunk_id": results['ids'][0][idx],
                "text": results['documents'][0][idx],
                "source": filename,
                "page_number": results['metadatas'][0][idx]['page_number'],
                "similarity_score": similarity_score
            })
            
    print(f" 🚀 Tổng số mẩu tin hợp lệ gửi đi: {len(matched_chunks)}\n")
    return matched_chunks