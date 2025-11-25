import os
import argparse
from src.agents.file_system_agent import FileSystemAgent
from src.config import Config, LLMProvider

def main():
    parser = argparse.ArgumentParser(description="File System Context Agent")
    parser.add_argument("--query", type=str, help="Query to ask the agent")
    parser.add_argument("--add-docs", type=str, help="Directory path to add documents")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--provider", type=str, choices=["openai", "openrouter"], 
                        help="LLM provider to use (openai or openrouter)")
    parser.add_argument("--model", type=str, help="Model to use")
    
    args = parser.parse_args()
    
    # Determine LLM provider
    provider = None
    if args.provider:
        provider = LLMProvider(args.provider)
    
    # Initialize the agent
    agent = FileSystemAgent(llm_provider=provider, model=args.model)
    
    if args.add_docs:
        agent.add_documents(args.add_docs)
        return
    
    if args.query:
        response = agent.query(args.query)
        print(f"Response: {response}")
        return
    
    if args.interactive:
        print("File System Context Agent - Interactive Mode")
        print("Type 'exit' to quit.")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == "exit":
                break
            
            response = agent.query(user_input)
            print(f"Agent: {response}")
        return
    
    # If no arguments provided, print help
    parser.print_help()

if __name__ == "__main__":
    main()