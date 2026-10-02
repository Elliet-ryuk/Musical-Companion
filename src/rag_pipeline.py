from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq


# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

KNOWLEDGE_DIR = BASE_DIR / "knowledge"


# --------------------------------------------------
# Load all music knowledge
# --------------------------------------------------

loader = DirectoryLoader(
    str(KNOWLEDGE_DIR),
    glob="**/*.md",
    loader_cls=TextLoader
)

documents = loader.load()


# --------------------------------------------------
# Split documents into chunks
# --------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = text_splitter.split_documents(documents)


# --------------------------------------------------
# Create embeddings
# --------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# --------------------------------------------------
# Create FAISS vector database
# --------------------------------------------------

vectorstore = FAISS.from_documents(
    chunks,
    embeddings
)


# --------------------------------------------------
# Create retriever
# --------------------------------------------------

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
)


# --------------------------------------------------
# Groq LLM
# --------------------------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)