import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1" 
)

def generate_rag_answer(question: str, context_chunks: list) -> str:
    if not context_chunks:
        return "Xin lỗi, tôi không tìm thấy thông tin nào trong tài liệu để trả lời câu hỏi này."

    context_text = "\n\n".join([f"- Nguồn {c['source']} (Trang {c['page_number']}):\n{c['text']}" for c in context_chunks])

    prompt = f"""Bạn là một trợ lý ảo thông minh. Hãy trả lời câu hỏi của người dùng CHỈ DỰA VÀO phần Ngữ Cảnh được cung cấp dưới đây. Nếu Ngữ Cảnh không chứa thông tin, hãy nói bạn không biết.

    NGỮ CẢNH:
    {context_text}

    CÂU HỎI: {question}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant", 
        messages=[
            {"role": "system", "content": "Bạn là trợ lý RAG chuyên nghiệp. Hãy trả lời bằng tiếng Việt."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content