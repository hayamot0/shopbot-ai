import os 
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def load_rag_pipeline():

    embeddings=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001",task_type="retrieval_document")

    llm=ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    loader=DirectoryLoader("knowledge_base/",glob="*.txt",loader_cls=TextLoader)
    documents=loader.load()
    text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "،", " "]
        )

    chunks=text_splitter.split_documents(documents)
    FAISS_PATH = "faiss_db/"
    FAISS_INDEX = "faiss_shopbot"

    if os.path.exists(f"{FAISS_PATH}{FAISS_INDEX}.faiss"):
        vector_store = FAISS.load_local(
            FAISS_PATH, embeddings, FAISS_INDEX,
            allow_dangerous_deserialization=True)
    else:
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(FAISS_PATH, FAISS_INDEX)
    retriever=vector_store.as_retriever()

    template="""
    You are a helpful customer support assistant for ShopBot, an online clothing store.
    1. Use ONLY the following pieces of retrieved context to answer the question.
    2. If the answer is not in the context, say "Specifications for this query are unavailable."
    3. If the user is just greeting you (like saying "Hi" or "Hello"), respond politely as the shop's representative without looking at the context.
    ---
    context:
    {context}
    ---
    user question:
    {question}
    """

    prompt=ChatPromptTemplate.from_template(template)

    chain=(
        {"context":retriever,"question":RunnablePassthrough()}
        |prompt
        |llm
        |StrOutputParser()
    )

    return chain


