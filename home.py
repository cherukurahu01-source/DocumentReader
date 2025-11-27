import streamlit as st
from docx import Document
import time


def read_docx_form(file_path):
    doc = Document(file_path)   # <-- Correct!
    results = []
    form_data = {}

    # Extract paragraphs
    for para in doc.paragraphs:
        if para.text.strip():
            results.append(para.text.strip())

    # Extract tables (cell by cell)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text = cell.text.strip()
                if text:
                    results.append(text)
                    
    for line in results:
        if ":" in line:
            key, value = line.split(":",1)
            form_data[key.strip()] = value.strip()
            

    return form_data


def chat_stream(prompt):
    response = f'You said, "{prompt}" ...interesting.'
    for char in response:
        yield char
        time.sleep(0.02)


def save_feedback(index):
    st.session_state.history[index]["feedback"] = st.session_state[f"feedback_{index}"]

st.title("Document Extractor")


if "history" not in st.session_state:
    st.session_state.history = []

for i, message in enumerate(st.session_state.history):
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant":
            feedback = message.get("feedback", None)
            st.session_state[f"feedback_{i}"] = feedback
            st.feedback(
                "thumbs",
                key=f"feedback_{i}",
                disabled=feedback is not None,
                on_change=save_feedback,
                args=[i],
            )

if prompt := st.chat_input("Say something"):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        content = read_docx_form(prompt)
        response = st.table(content)
        st.feedback(
            "thumbs",
            key=f"feedback_{len(st.session_state.history)}",
            on_change=save_feedback,
            args=[len(st.session_state.history)],
        )
    st.session_state.history.append({"role": "assistant", "content":  content })