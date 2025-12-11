#!/usr/bin/env python3
"""
AWS Infrastructure Advisor - Single Agent Consultant.

An AI-powered AWS consultant that uses official AWS documentation and multiple
MCP servers to provide expert guidance on AWS infrastructure.

Architecture:
Single Claude-based agent with access to 4 MCP servers:
- AWS Documentation MCP Server (official AWS docs)
- Terraform MCP Server (Terraform Registry)
- AWS CDK MCP Server (CDK constructs and patterns)
- AWS Pricing MCP Server (real-time AWS pricing)

The agent acts as a general AWS consultant that can answer questions,
provide architecture guidance, generate code, and estimate costs.
"""

import sys
import os
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional

from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp import MCPClient
from strands.models.ollama import OllamaModel

from agents.aws_consultant import AWSConsultant
from agents.config import (
    get_mcp_servers_with_profile,
    OLLAMA_HOST,
    OLLAMA_MODEL_ID,
    OLLAMA_MAX_TOKENS,
    OLLAMA_TEMPERATURE,
    OLLAMA_KEEP_ALIVE
)


class MCPClientManager:
    """
    Manages MCP client lifecycle for a specific MCP server.
    """
    
    def __init__(self, server_name: str, config: Dict):
        """
        Initialize the MCP client manager.
        
        Args:
            server_name: Name of the MCP server
            config: Configuration dictionary with command, args, and env
        """
        self.server_name = server_name
        self.command = config["command"]
        self.args = config["args"]
        self.env = config.get("env", {})
        self.client = self._create_client()
    
    def _create_client(self) -> MCPClient:
        """Create the MCP client instance."""
        return MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command=self.command,
                args=self.args,
                env=self.env
            )
        ))
    
    def __enter__(self):
        """Enter context manager."""
        self.client.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        return self.client.__exit__(exc_type, exc_val, exc_tb)
    
    def list_tools(self) -> List:
        """Get the list of available tools from the MCP server."""
        return self.client.list_tools_sync()


class ConversationManager:
    """
    Manages conversation history and output.
    """
    
    def __init__(self):
        """Initialize the conversation manager."""
        self.history: List[Dict[str, str]] = []
    
    def add_exchange(self, user_input: str, assistant_response: str) -> None:
        """Add a conversation exchange to history."""
        self.history.append({
            "user": user_input,
            "assistant": assistant_response,
            "timestamp": time.time()
        })
    
    def save_conversation(
        self,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Save conversation to a file.
        
        Args:
            filename: Optional filename, auto-generated if not provided
            
        Returns:
            Path to saved file, or None if failed
        """
        if not self.history:
            return None
        
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        if filename is None:
            timestamp = int(time.time())
            filename = f"aws_consultation_{timestamp}.txt"
        
        output_file = output_dir / filename
        
        try:
            with open(output_file, 'w', encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("AWS INFRASTRUCTURE ADVISOR - CONSULTATION LOG\n")
                f.write("=" * 80 + "\n\n")
                
                for i, exchange in enumerate(self.history, 1):
                    f.write(f"\n{'=' * 80}\n")
                    f.write(f"Exchange {i}\n")
                    f.write(f"{'=' * 80}\n\n")
                    f.write(f"USER:\n{exchange['user']}\n\n")
                    f.write(f"CONSULTANT:\n{exchange['assistant']}\n")
                
                f.write(f"\n{'=' * 80}\n")
                f.write("END OF CONSULTATION\n")
                f.write(f"{'=' * 80}\n")
            
            return str(output_file)
        except Exception as e:
            print(f"\n⚠️  Warning: Could not save conversation: {e}")
            return None


def print_welcome(use_local: bool = False, model_name: str = "Claude"):
    """
    Print welcome message.
    
    Args:
        use_local: Whether using local Ollama model
        model_name: Name of the model being used
    """
    print("\n" + "=" * 80)
    print("☁️  AWS INFRASTRUCTURE ADVISOR")
    print("=" * 80)
    
    if use_local:
        print(f"\n🖥️  Running with local model: {model_name}")
    else:
        print(f"\n☁️  Running with {model_name} via AWS Bedrock")
    
    print("\nYour AI-powered AWS consultant with access to:")
    print("  📚 Official AWS Documentation")
    print("  🔧 Terraform Registry")
    print("  🏗️  AWS CDK Resources")
    print("  💰 Real-time AWS Pricing")
    print("\nI can help you with:")
    print("  • AWS architecture and design questions")
    print("  • Best practices and recommendations")
    print("  • Terraform and CDK code generation")
    print("  • Cost estimation and optimization")
    print("  • Service comparisons and selection")
    print("\nType your questions or requests. Type 'exit', 'quit', or 'bye' to end.")
    print("=" * 80 + "\n")


def interactive_mode(consultant: AWSConsultant, use_local: bool = False, model_name: str = "Claude") -> ConversationManager:
    """
    Run the consultant in interactive mode.
    
    Args:
        consultant: The AWS consultant agent
        use_local: Whether using local Ollama model
        model_name: Name of the model being used
        
    Returns:
        ConversationManager with the conversation history
    """
    conversation = ConversationManager()
    
    print_welcome(use_local, model_name)
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                print("\n👋 Thank you for using AWS Infrastructure Advisor!")
                break
            
            if not user_input:
                continue
            
            # Get consultant response
            print("\n🤔 Consulting AWS resources...\n")
            response = consultant.consult(user_input)
            
            # Display response
            print(f"AWS Consultant:\n{response}\n")
            print("-" * 80 + "\n")
            
            # Save to conversation history
            conversation.add_exchange(user_input, response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Consultation interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue
    
    return conversation


def single_query_mode(consultant: AWSConsultant, query: str, use_local: bool = False, model_name: str = "Claude") -> str:
    """
    Process a single query and return the response.
    
    Args:
        consultant: The AWS consultant agent
        query: The user's query
        use_local: Whether using local Ollama model
        model_name: Name of the model being used
        
    Returns:
        The consultant's response
    """
    print("\n" + "=" * 80)
    print("☁️  AWS INFRASTRUCTURE ADVISOR")
    print("=" * 80)
    
    if use_local:
        print(f"🖥️  Using local model: {model_name}")
    else:
        print(f"☁️  Using {model_name} via AWS Bedrock")
    
    print(f"\nQuery: {query}\n")
    print("🤔 Consulting AWS resources...\n")
    
    response = consultant.consult(query)
    
    print("=" * 80)
    print("RESPONSE")
    print("=" * 80)
    print(f"\n{response}\n")
    
    return response


def main() -> int:
    """
    Main entry point for the AWS Infrastructure Advisor.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="AWS Infrastructure Advisor - AI-powered AWS Consultant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                          # Interactive mode (Claude via Bedrock)
  python main.py --local                                  # Interactive mode (local Ollama model)
  python main.py "How do I set up a serverless API?"     # Single query mode
  python main.py --local "Get EC2 pricing"                # Single query with local model
  python main.py --aws-profile prod "Get EC2 pricing"    # With AWS profile
        """
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Your AWS question (optional, omit for interactive mode)"
    )
    parser.add_argument(
        "--aws-profile",
        default=None,
        help="AWS profile to use (default: uses default profile or AWS_PROFILE env var)"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help=f"Use local Ollama model ({OLLAMA_MODEL_ID}) instead of Claude via Bedrock"
    )
    
    args = parser.parse_args()
    
    # Determine AWS profile
    aws_profile = args.aws_profile or os.environ.get("AWS_PROFILE", "default")
    
        # Determine which model to use
    use_local = args.local
    model_instance = None
    model_name = "Claude"
    
    if use_local:
        print(f"\n🖥️  Initializing local Ollama model: {OLLAMA_MODEL_ID}")
        print(f"   Host: {OLLAMA_HOST}")
        print(f"   Make sure Ollama is running (ollama serve)\n")
        
        try:
            model_instance = OllamaModel(
                host=OLLAMA_HOST,
                model_id=OLLAMA_MODEL_ID,
                max_tokens=OLLAMA_MAX_TOKENS,
                temperature=OLLAMA_TEMPERATURE,
                keep_alive=OLLAMA_KEEP_ALIVE,
            )
            model_name = OLLAMA_MODEL_ID
        except Exception as e:
            print(f"❌ Error initializing Ollama model: {e}")
            print("\n⚠️  Troubleshooting:")
            print("   1. Install Ollama: https://ollama.ai")
            print(f"   2. Pull the model: ollama pull {OLLAMA_MODEL_ID}")
            print("   3. Start Ollama: ollama serve")
            return 1
    else:
        print(f"\n☁️  Using Claude via AWS Bedrock")
        print(f"   Using AWS profile: {aws_profile}\n")
    
    # Get MCP server configurations with the specified AWS profile
    mcp_servers = get_mcp_servers_with_profile(aws_profile)
    
    print("🔌 Connecting to MCP servers...")
    if not use_local:
        print(f"   Using AWS profile: {aws_profile}")
    print("   (This may take a moment on first run...)\n")
    
    try:
        # Connect to all MCP servers
        with MCPClientManager("documentation", mcp_servers["documentation"]) \
                as doc_mcp, \
             MCPClientManager("terraform", mcp_servers["terraform"]) \
                as tf_mcp, \
             MCPClientManager("cdk", mcp_servers["cdk"]) as cdk_mcp, \
             MCPClientManager("pricing", mcp_servers["pricing"]) \
                as pricing_mcp:
            
            # Get tools from each server
            print("   Loading AWS Documentation tools...")
            documentation_tools = doc_mcp.list_tools()
            
            print("   Loading Terraform tools...")
            terraform_tools = tf_mcp.list_tools()
            
            print("   Loading CDK tools...")
            cdk_tools = cdk_mcp.list_tools()
            
            print("   Loading AWS Pricing tools...")
            pricing_tools = pricing_mcp.list_tools()
            
            # Combine all tools
            all_tools = (
                documentation_tools +
                terraform_tools +
                cdk_tools +
                pricing_tools
            )
            
            print(f"\n✅ Connected successfully!")
            print(f"   • AWS Documentation: {len(documentation_tools)} tools")
            print(f"   • Terraform: {len(terraform_tools)} tools")
            print(f"   • CDK: {len(cdk_tools)} tools")
            print(f"   • AWS Pricing: {len(pricing_tools)} tools")
            print(f"   • Total: {len(all_tools)} tools available\n")
            
            # Create the AWS consultant with the appropriate model
            consultant = AWSConsultant(all_tools, model=model_instance)
            
            # Determine mode: interactive or single query
            if args.query:
                # Single query mode
                query = " ".join(args.query)
                response = single_query_mode(consultant, query, use_local, model_name)
                
                # Save to file
                conversation = ConversationManager()
                conversation.add_exchange(query, response)
                output_file = conversation.save_conversation()
                if output_file:
                    print(f"💾 Consultation saved to: {output_file}\n")
            else:
                # Interactive mode
                conversation = interactive_mode(consultant, use_local, model_name)
                
                # Save conversation
                if conversation.history:
                    output_file = conversation.save_conversation()
                    if output_file:
                        print(f"\n💾 Conversation saved to: {output_file}")
            
            return 0
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n⚠️  Troubleshooting:")
        if use_local:
            print("   1. Install Ollama: https://ollama.ai")
            print(f"   2. Pull the model: ollama pull {OLLAMA_MODEL_ID}")
            print("   3. Start Ollama: ollama serve")
            print("   4. Install dependencies: pip install -r requirements.txt")
        else:
            print("   1. Configure AWS credentials: aws configure")
            print("   2. Install dependencies: pip install -r requirements.txt")
            print("   3. Check AWS profile is valid")
        return 1


if __name__ == "__main__":
    sys.exit(main())
