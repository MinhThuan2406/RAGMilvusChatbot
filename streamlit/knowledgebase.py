import os
import streamlit as st
from pathlib import Path
from mimetypes import guess_type

st.set_page_config(page_title="Knowledge Base Viewer", layout="wide")

st.markdown(
    "<style>" + open("styles/knowledgebase.css").read() + "</style>",
    unsafe_allow_html=True
)

RAW_DOCS_DIR = Path("./data/raw_docs")
VALID_EXTENSIONS = [".pdf", ".doc", ".docx", ".txt", ".jpg", ".jpeg", ".png"]

def get_all_files(folder: Path):
    return [f for f in folder.iterdir() if f.suffix.lower() in VALID_EXTENSIONS]

def display_file_preview(file: Path):
    ext = file.suffix.lower()
    st.write(f"**{file.name}**")
    st.caption(f"{file}")
    if ext in [".jpg", ".jpeg", ".png"]:
        st.image(file, use_container_width=True)
    elif ext == ".txt":
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            st.text(f.read())
    elif ext == ".pdf":
        st.download_button("Download PDF", data=file.read_bytes(), file_name=file.name, use_container_width=True)
        st.markdown("Preview not available. Use download button above.")
    elif ext in [".doc", ".docx"]:
        st.download_button("Download Word File", data=file.read_bytes(), file_name=file.name, use_container_width=True)
        st.markdown("Preview not available. Use download button above.")
    st.divider()

st.sidebar.title("File Navigator")

all_files = get_all_files(RAW_DOCS_DIR)
file_types = {ext.strip("."): 0 for ext in VALID_EXTENSIONS}
file_names = [f.name for f in all_files]
selected_file = st.sidebar.selectbox("Select a file", options=file_names)

for file in all_files:
    ext = file.suffix.lower().strip(".")
    if ext in file_types:
        file_types[ext] += 1

st.sidebar.markdown("### File Statistics")
st.sidebar.markdown(f"**Total files:** {len(all_files)}")
for ext, count in file_types.items():
    if count > 0:
        st.sidebar.markdown(f"{ext.upper()}: {count}")

st.title("Knowledge Base Viewer")
st.text_input("Search files", placeholder="Enter file name or keyword...", key="search_box")

cols = st.columns(3)

for i, file in enumerate(all_files):
    with cols[i % 3]:
        ext = file.suffix.lower()
        if file.name == selected_file and ext not in [".pdf"]:
            st.markdown(
                "<div style='border: 2px solid #6c63ff; padding: 12px; border-radius: 8px; margin-bottom: 16px;'>",
                unsafe_allow_html=True
            )
            display_file_preview(file)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            display_file_preview(file)
