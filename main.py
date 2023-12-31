import os

import google.generativeai as palm
import numpy as np
import streamlit as st
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import GooglePalmEmbeddings
from langchain.llms import GooglePalm
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from PyPDF2 import PdfReader

os.environ['GOOGLE_API_KEY'] =  'AIzaSyCnrC5dOS1PLWkqaykfhhtVNCY0is9hvg8'

def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader= PdfReader(pdf)
        for page in pdf_reader.pages:
            text+= page.extract_text()
    return  text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GooglePalmEmbeddings()
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vector_store

def get_conversational_chain(vector_store):
    llm=GooglePalm()
    memory = ConversationBufferMemory(memory_key = "chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vector_store.as_retriever(), memory=memory)
    return conversation_chain

def user_input(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chatHistory = response['chat_history']
    for i, message in enumerate(st.session_state.chatHistory):
        if i%2 == 0:
            st.write("Your Question : ", message.content)
        else:
            st.write("Relevent Answer: ", message.content)
def main():
    st.set_page_config("EXAM-CHEAT-BUDDY")
    # st.image(image, channels="BGR")
    st.header("EXAM CHEATER AI CHAT BOT 💬")
    user_question = st.text_input("Ask me any question form the data from the uploaded pdf")
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chatHistory" not in st.session_state:
        st.session_state.chatHistory = None
    if user_question:
        user_input(user_question)
    with st.sidebar:
        st.title("Settings")
        st.subheader("Upload your Documents")
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Process Button", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                vector_store = get_vector_store(text_chunks)
                st.session_state.conversation = get_conversational_chain(vector_store)
                st.success("Done")

    st.markdown(
    '<style>'
    '.made-with-love {'
    '    background-color: rgb(14,17,23);; /* Dark background color */'
    '    color: #ffffff; /* White text color */'
    '    text-align: center;'
    '    padding: 10px;'
    '    bottom: 0;'
    '    width: 100%;'
    '}'
    '</style>'
    '<div class="made-with-love">Made with ❤️ by Krish Makhijani</div>'
, unsafe_allow_html=True)

if __name__ == "__main__":
    main()