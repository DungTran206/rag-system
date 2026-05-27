import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="RAG WorkStation", page_icon="🤖", layout="wide")
st.title("🤖 Chatbot RAG - Quản lý Tài liệu Nâng cao")

def fetch_uploaded_files():
    try:
        res = requests.get(f"{API_URL}/ingest/files")
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

existing_files = fetch_uploaded_files()

with st.sidebar:
    st.header("📂 Quản lý Tài liệu")
    uploaded_file = st.file_uploader("Tải file PDF mới", type=["pdf"])
    
    if st.button("Nạp dữ liệu", use_container_width=True):
        if uploaded_file is not None:
            with st.spinner("Đang xử lý..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                res = requests.post(f"{API_URL}/ingest/", files=files)
                if res.status_code == 200:
                    st.success("Nạp thành công!")
                    st.rerun()
        else:
            st.warning("Vui lòng chọn file!")

    st.divider()
    st.subheader("📋 Danh sách file đã nạp:")
    
    if not existing_files:
        st.info("Chưa có tài liệu nào trong hệ thống.")
    else:
        for filename in existing_files:
            col1, col2 = st.columns([3, 1])
            col1.text(f"📄 {filename[:20]}..." if len(filename) > 20 else f"📄 {filename}")
            if col2.button("Xóa", key=f"del_{filename}", type="primary"):
                with st.spinner("Đang xóa..."):
                    del_res = requests.delete(f"{API_URL}/ingest/files/{filename}")
                    
                    if del_res.status_code == 200:
                        st.success("Đã xóa!")
                        st.rerun() 
                    else:
                        error_msg = del_res.json().get("detail", "Lỗi không xác định")
                        st.error(f"Thất bại: {error_msg}")

selected_file_filter = None
if existing_files:
    options = ["Hỏi trên tất cả tài liệu"] + existing_files
    choice = st.selectbox("🎯 Bạn muốn hỏi dựa trên tài liệu nào?", options)
    if choice != "Hỏi trên tất cả tài liệu":
        selected_file_filter = choice

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Đang lục tìm tài liệu..."):
            try:
                payload = {"question": prompt, "file_filter": selected_file_filter}
                res = requests.post(f"{API_URL}/query/", json=payload)
                
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "")
                    sources = data.get("sources", [])

                    st.markdown(answer)

                    if sources:
                        with st.expander("📚 Xem nguồn trích dẫn"):
                            for idx, src in enumerate(sources):
                                st.markdown(f"**[{idx+1}] File:** `{src['source_file']}` | **Trang:** `{src['page_number']}` | **Độ tin cậy:** `{src['similarity_score']*100:.1f}%`")
                    
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Lỗi: {res.json().get('detail')}")
            except Exception as e:
                st.error("Lỗi kết nối Backend API!")