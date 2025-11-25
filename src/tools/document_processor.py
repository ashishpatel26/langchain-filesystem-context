# src/tools/document_processor.py

from typing import List, Dict, Any
from langchain.tools import BaseTool
from pydantic import Field
from src.utils.file_indexer import FileIndexer

class DocumentSearchTool(BaseTool):
    """Tool for searching documents in the vector store."""
    
    name: str = "document_search"
    description: str = "Use this tool to search for relevant documents based on a query. Input should be the search query."
    
    file_indexer: FileIndexer = Field(exclude=True)
    
    def __init__(self, file_indexer: FileIndexer, **kwargs):
        super().__init__(file_indexer=file_indexer, **kwargs)
    
    def _run(self, query: str) -> str:
        """Execute the tool to search for documents."""
        # --- DEBUGGING LINE ---
        print(f"--- TOOL CALLED with query: {query} ---")
        
        try:
            results = self.file_indexer.search(query, k=3)
            
            if not results:
                # --- DEBUGGING LINE ---
                print("--- TOOL RETURNED NO RESULTS ---")
                return "No relevant documents found for the query."
            
            output = "Found the following relevant documents:\n\n"
            
            for i, doc in enumerate(results, 1):
                source = doc.metadata.get("source", "Unknown")
                content = doc.page_content
                
                output += f"Document {i} (Source: {source}):\n"
                output += f"{content}\n\n"
            
            return output
        except Exception as e:
            # --- DEBUGGING LINE ---
            print(f"--- TOOL ERRORED: {str(e)} ---")
            return f"Error searching for documents: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Execute the tool asynchronously."""
        return self._run(query)