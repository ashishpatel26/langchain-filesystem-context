# src/agents/file_system_agent.py

import os
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_tool_calling_agent # <--- CHANGE HERE
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from src.tools.file_reader import FileReaderTool
from src.tools.document_processor import DocumentSearchTool
from src.utils.file_indexer import FileIndexer
from src.utils.llm_factory import create_llm
from src.config import Config, LLMProvider

class FileSystemAgent:
    """An agent that can use the file system as context."""
    
    def __init__(self, llm_provider: LLMProvider = None, model: str = None):
        # Initialize LLM
        self.llm = create_llm(provider=llm_provider, model=model)
        
        # Initialize file indexer
        self.file_indexer = FileIndexer()
        
        # Check if vector store exists
        if os.path.exists(Config.VECTOR_DB_PATH):
            self.file_indexer.load_vector_store(Config.VECTOR_DB_PATH)
            print("Loaded existing vector store.")
        else:
            self._initialize_vector_store()
        
        # Initialize tools
        self.tools = [
            FileReaderTool(file_indexer=self.file_indexer),
            DocumentSearchTool(file_indexer=self.file_indexer)
        ]
        
        # Create the agent
        self.agent_executor = self._create_agent()
    
    def _initialize_vector_store(self):
        """Initialize the vector store with documents from the file system."""
        print("Initializing vector store...")
        
        # Load documents from directories
        documents = []
        
        if os.path.exists(Config.DOCUMENTS_DIR):
            documents.extend(self.file_indexer.load_documents(Config.DOCUMENTS_DIR))
        
        if os.path.exists(Config.FILES_DIR):
            documents.extend(self.file_indexer.load_documents(Config.FILES_DIR))
        
        if not documents:
            print("No documents found. Creating empty vector store.")
            self.file_indexer.create_vector_store([])
            return
        
        # Process documents
        processed_docs = self.file_indexer.process_documents(documents)
        
        # Create vector store
        self.file_indexer.create_vector_store(processed_docs)
        
        # Save vector store
        os.makedirs(os.path.dirname(Config.VECTOR_DB_PATH), exist_ok=True)
        self.file_indexer.save_vector_store(Config.VECTOR_DB_PATH)
        
        print(f"Vector store initialized with {len(processed_docs)} document chunks.")
    
    def _create_agent(self):
        """Create the agent with the specified tools and prompt."""
        # Define a much more forceful, step-by-step prompt (ReAct style)
        system_prompt = """
        You are an AI assistant that answers questions ONLY by using the provided tools.
        You have access to these tools:
        1. `document_search`: To find relevant document chunks.
        2. `file_reader`: To read the full content of a file.

        Follow this process for every question:
        1. Use the `document_search` tool with the user's question as the query.
        2. Review the results from the search tool.
        3. Formulate your answer based ONLY on the information provided by the tool.
        4. If the search results are empty, state that you could not find any information in the files.
        
        **Do not answer from your general knowledge. Your entire response must be based on the output of the tools.**
        """
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_tool_calling_agent( # <--- CHANGE HERE
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create the agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def query(self, question: str) -> str:
        """Query the agent with a question."""
        response = self.agent_executor.invoke({"input": question})
        return response.get("output", "No response generated.")
    
    def add_documents(self, directory: str) -> None:
        """Add documents from a directory to the vector store."""
        # Load new documents
        new_documents = self.file_indexer.load_documents(directory)
        
        if not new_documents:
            print("No new documents found.")
            return
        
        # Process documents
        processed_docs = self.file_indexer.process_documents(new_documents)
        
        # Add to vector store
        if self.file_indexer.vector_store:
            self.file_indexer.vector_store.add_documents(processed_docs)
        else:
            self.file_indexer.create_vector_store(processed_docs)
        
        # Save updated vector store
        self.file_indexer.save_vector_store(Config.VECTOR_DB_PATH)
        
        print(f"Added {len(processed_docs)} document chunks to the vector store.")