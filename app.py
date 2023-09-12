
# Streamlit library, used to create the user interface for the application.
import streamlit as st
# Module from the Langchain library that provides embeddings for text processing using OpenAI language models.
from langchain.embeddings.openai import OpenAIEmbeddings
# Python built-in module for handling temporary files.
import tempfile
# Python built-in module for time-related operations.
import time
# Below are the classes from the Langchain library
from langchain import OpenAI, PromptTemplate, LLMChain
# class from the Langchain library that splits text into smaller chunks based on specified parameters.
from langchain.text_splitter import CharacterTextSplitter
# This is a class from the Langchain library that loads PDF documents and splits them into pages.
from langchain.document_loaders import PyPDFLoader
# This is a function from the Langchain library that loads a summarization chain for generating summaries.
from langchain.chains.summarize import load_summarize_chain
# This is a class from the Langchain library that represents a document.
from langchain.docstore.document import Document
# This is a class from the Langchain library that provides vector indexing and similarity search using FAISS.
from langchain.vectorstores import FAISS
# This is a function from the Langchain library that loads a question-answering chain for generating answers to questions.
from langchain.chains.question_answering import load_qa_chain 
import openai
llm = OpenAI(openai_api_key = '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', temperature=0.2)
# We need to split the text using Character Text Split such that it should not increase token size
text_splitter = CharacterTextSplitter(
    separator = "\n",
    chunk_size = 800,
    chunk_overlap  = 200,
    length_function = len,
)

with st.sidebar:
    st.title('BlackBox.AI')
    st.markdown('''       
    ## PDF: Summarizer & QA
    The application employs generative AI models to process PDF content and provide responses, with Langchain components handling various tasks like text splitting and document loading. It features a user-friendly interface with informative sidebars.
    ## Our Work
    Currently, we deployed the generative AI model to provide answers to queries based on a PDF document's content, including its summary properties. It's crucial to keep in mind that general question-answering tasks are not the primary focus of generative AI models . Instead, they are intended for the production of human-like writing.
    We'll create a virtual assistant in the future for engaging user experiences.
    ## About
    The application employs generative AI models to process PDF content and provide responses,
    with Langchain components handling various tasks like text splitting and 
    document loading. It features a user-friendly interface with informative sidebars.''')

st.title("PDF: Summarizer & QA")
pdf_file = st.file_uploader("Choose a PDF file", type="pdf")
if pdf_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(pdf_file.read())
        pdf_path = tmp_file.name
        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split()
    # User input for page selection
    page_selection = st.radio("Page selection", ["Single page", "Page range", "Overall Summary", "Question"])
    if page_selection == "Single page":
        page_number = st.number_input("Enter page number", min_value=1, max_value=len(pages), value=1, step=1)
        view = pages[page_number - 1]
        texts = text_splitter.split_text(view.page_content)
        docs = [Document(page_content=t) for t in texts]
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        summaries = chain.run(docs)

        st.subheader("Summary")
        st.write(summaries)
    elif page_selection == "Page range":
            start_page = st.number_input("Enter start page", min_value=1, max_value=len(pages), value=1, step=1)
            end_page = st.number_input("Enter end page", min_value=start_page, max_value=len(pages), value=start_page, step=1)

            texts = []
            for page_number in range(start_page, end_page+1):
                view = pages[page_number-1]
                page_texts = text_splitter.split_text(view.page_content)
                texts.extend(page_texts)
            docs = [Document(page_content=t) for t in texts]
            chain = load_summarize_chain(llm, chain_type="map_reduce")
            summaries = chain.run(docs)
            st.subheader("Summary")
            st.write(summaries)

    elif page_selection == "Overall Summary":
        combined_content = ''.join([p.page_content for p in pages])  # we get entire page data
        texts = text_splitter.split_text(combined_content)
        docs = [Document(page_content=t) for t in texts]
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        summaries = chain.run(docs)
        st.subheader("Summary")
        st.write(summaries)
    elif page_selection == "Question":
        question = st.text_input("Enter your question")
        combined_content = ''.join([p.page_content for p in pages])
        texts = text_splitter.split_text(combined_content)
        embedding = OpenAIEmbeddings(openai_api_key = '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')
        document_search = FAISS.from_texts(texts, embedding)
        chain = load_qa_chain(llm, chain_type="stuff")
        docs = document_search.similarity_search(question)
        summaries = chain.run(input_documents=docs, question=question)
        st.write(summaries)
    else:
        time.sleep(30)
        st.warning("No PDF file uploaded")

try:
    if 'pages' not in locals() and 'pages' not in globals():
        st.warning("No PDF file uploaded, Please upload !!")    
    # Rest of your code that uses the 'pages' variable
    # ...
except NameError:
    st.warning("No PDF file uploaded")
