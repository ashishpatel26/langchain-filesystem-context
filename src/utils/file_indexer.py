# src/utils/file_indexer.py

import os
import pickle
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from src.config import Config

class FileIndexer:
    def __init__(self):
        # Ensure the API key is available
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
            
        self.embeddings = OpenAIEmbeddings(openai_api_key=Config.OPENAI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        self.vector_store = None
        self.file_metadata = {}
        
    def load_documents(self, directory: str) -> List[Document]:
        """Load documents from the specified directory."""
        documents = []
        
        if not os.path.exists(directory):
            print(f"Warning: Directory {directory} does not exist.")
            return documents
            
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            try:
                if filename.endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                elif filename.endswith(".txt"):
                    loader = TextLoader(file_path, encoding='utf-8')
                else:
                    # Use UnstructuredFileLoader for other file types
                    loader = UnstructuredFileLoader(file_path)
                    
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = filename
                    doc.metadata["file_path"] = file_path
                    
                documents.extend(docs)
                self.file_metadata[filename] = {
                    "file_path": file_path,
                    "file_type": os.path.splitext(filename)[1],
                    "size": os.path.getsize(file_path)
                }
            except Exception as e:
                print(f"Error loading file {filename}: {e}")
            
        return documents
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """Process documents by splitting them into chunks."""
        return self.text_splitter.split_documents(documents)
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Create a FAISS vector store from the documents."""
        if not documents:
            print("Warning: No documents provided to create vector store. Creating an empty one.")
            # Create a dummy document to avoid errors with an empty FAISS index
            dummy_doc = Document(page_content="empty", metadata={"source": "empty"})
            documents = [dummy_doc]
            
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        return self.vector_store
    
    def save_vector_store(self, path: str) -> None:
        """Save the vector store to disk."""
        if self.vector_store:
            os.makedirs(path, exist_ok=True)
            self.vector_store.save_local(path)
            
            # Save metadata
            with open(os.path.join(path, "file_metadata.pkl"), "wb") as f:
                pickle.dump(self.file_metadata, f)
    
    def load_vector_store(self, path: str) -> FAISS:
        """Load the vector store from disk."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Vector store not found at {path}")
            
        self.vector_store = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
        
        # Load metadata
        with open(os.path.join(path, "file_metadata.pkl"), "rb") as f:
            self.file_metadata = pickle.load(f)
            
        return self.vector_store
    
    def search(self, query: str, k: int = 4) -> List[Document]:
        """Search for documents similar to the query."""
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Please create or load a vector store first.")
            
        return self.vector_store.similarity_search(query, k=k)
    
    def get_file_metadata(self, filename: str) -> Dict[str, Any]:
        """Get metadata for a specific file."""
        return self.file_metadata.get(filename, {})