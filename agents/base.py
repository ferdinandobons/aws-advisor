"""
Base agent class for AWS Infrastructure Advisor.

Provides a simple base class for creating Claude-based agents with MCP tools.
"""

from typing import Optional, List, Any
from strands import Agent


class AWSConsultantAgent:
    """
    AWS Consultant Agent powered by Claude via AWS Bedrock with MCP tools.
    
    This agent acts as a general AWS consultant that can:
    - Answer AWS-related questions using official documentation
    - Generate infrastructure code (Terraform/CDK)
    - Estimate costs
    - Provide architecture guidance
    
    Uses Claude via AWS Bedrock with access to multiple MCP servers.
    """
    
    def __init__(self, system_prompt: str, tools: Optional[List] = None):
        """
        Initialize the AWS consultant agent.
        
        Args:
            system_prompt: The system prompt for the agent
            tools: List of MCP tools available to the agent
        """
        if not system_prompt or not system_prompt.strip():
            raise ValueError("system_prompt cannot be empty")
        
        self.system_prompt = system_prompt
        self.tools = tools or []
        self._agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """
        Create the underlying Strands agent instance.
        
        Returns:
            Configured Agent instance with Claude via Bedrock and MCP tools
        """
        agent_config = {
            'system_prompt': self.system_prompt,
            'model': None,  # None uses default model (Claude via AWS Bedrock)
        }
        
        if self.tools:
            agent_config['tools'] = self.tools
        
        return Agent(**agent_config)
    
    def ask(self, question: str) -> str:
        """
        Ask the agent a question or give it a task.
        
        Args:
            question: The user's question or request
            
        Returns:
            Agent's response as string
            
        Raises:
            ValueError: If question is empty
        """
        if not question or not question.strip():
            raise ValueError("question cannot be empty")
        
        try:
            response = self._agent(question)
            return str(response)
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def __repr__(self) -> str:
        """Return string representation of the agent."""
        return f"AWSConsultantAgent(tools={len(self.tools)})"
    
    def __str__(self) -> str:
        """Return user-friendly string representation."""
        return f"AWS Consultant Agent with {len(self.tools)} MCP tool(s)"
