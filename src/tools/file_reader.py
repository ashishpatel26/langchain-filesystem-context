# src/tools/file_reader.py

import os
from typing import Dict, Any
from langchain.tools import BaseTool
from pydantic import Field
from src.utils.file_indexer import FileIndexer

class FileReaderTool(BaseTool):
    """Tool for reading files from the file system."""
    
    name: str = "file_reader"
    description: str = "Use this tool to read the content of files from the file system. Input should be the filename."
    
    file_indexer: FileIndexer = Field(exclude=True)
    
    def __init__(self, file_indexer: FileIndexer, **kwargs):
        super().__init__(file_indexer=file_indexer, **kwargs)
    
    def _run(self, filename: str) -> str:
        """Execute the tool to read a file."""
        file_metadata = self.file_indexer.get_file_metadata(filename)
        
        if not file_metadata:
            return f"Error: File '{filename}' not found in the indexed files."
        
        file_path = file_metadata["file_path"]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except Exception as e:
            return f"Error reading file '{filename}': {str(e)}"
    
    async def _arun(self, filename: str) -> str:
        """Execute the tool asynchronously."""
        return self._run(filename)