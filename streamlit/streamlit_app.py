# This code is just for testing purposes

# import streamlit as st
# import requests

# st.set_page_config(page_title="RAGChatbot")

# st.title("RAGChatbot")

# provider = st.selectbox(
#     "Choose LLM Provider",
#     options=["ollama", "openai"],
#     format_func=lambda x: "Ollama (Llama3.2)" if x == "ollama" else "OpenAI (GPT-3.5/4)"
# )

# query = st.text_area("Ask your question:")

# if "history" not in st.session_state:
#     st.session_state["history"] = []


# file_name = st.text_input("(Optional) Only use context from this file:")
# if st.button("Ask"):
#     if not query.strip():
#         st.warning("Please enter a question.")
#     else:
#         payload = {"query": query, "provider": provider}
#         if file_name.strip():
#             payload["file_name"] = file_name.strip()
#         try:
#             response = requests.post("http://localhost:8001/api/chat/", json=payload, timeout=60)
#             response.raise_for_status()
#             answer = response.json().get("answer", "")
#             st.session_state["history"].append((provider, query, answer))
#         except Exception as e:
#             st.error(f"Error: {e}")

# if st.session_state["history"]:
#     st.markdown("### Chat History")
#     for prov, q, a in reversed(st.session_state["history"]):
#         st.markdown(f"**Provider:** `{prov}`\n\n**You:** {q}\n\n**Bot:** {a}\n---")

# st.markdown("---")
# st.caption("Powered by FastAPI backend, Ollama, and OpenAI.")