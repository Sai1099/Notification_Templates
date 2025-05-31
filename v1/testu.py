import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Recommendation System",
    page_icon=":fire:",
    layout="wide",
    initial_sidebar_state="expanded",
)


if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Chat Bot")
left_col, right_col = st.columns(2)

with left_col:
    st.header("File Upload")
    upload_file = st.file_uploader("Upload Your File:", type=['csv'])
    
    if upload_file is not None:
        st.success("File Uploaded Successfully")
        df = pd.read_csv(upload_file)
        st.subheader("File Preview")
        st.dataframe(df.head(5))
        
        if st.button("Start Analysis"):
            from data_massive import compute_file

            with st.spinner("Processing the file..."):
                result = compute_file(upload_file)
            
            st.session_state.messages.append({
                "role": "user",
                "content": f"Analyze data from {upload_file.name}"
            })
            st.session_state.messages.append({
                "role": "assistant",
                "content": result
            })

            st.rerun()
    else:
        st.info("Please upload a CSV file to begin.")

with right_col:
    st.header("Chat History")
    
    if st.session_state.messages:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    else:
        st.write("Waiting for file upload. Click 'Start Analysis' after uploading to begin.")
