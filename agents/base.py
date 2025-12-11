"""
Base agent class for AWS Infrastructure Advisor.

Provides base classes for creating agents with MCP tools using either
Anthropic (Claude via Bedrock) or Ollama (local models).
"""

from typing import Optional, List, Any
from strands import Agent
from strands.models.ollama import OllamaModel


class AWSConsultantAgent:
    """
    AWS Consultant Agent powered by Claude via AWS Bedrock or Ollama with MCP tools.
    
    This agent acts as a general AWS consultant that can:
    - Answer AWS-related questions using official documentation
    - Generate infrastructure code (Terraform/CDK)
    - Estimate costs
    - Provide architecture guidance
    
    Supports both Anthropic (Claude via Bedrock) and Ollama (local models).
    """
    
    def __init__(
        self,
        system_prompt: str,
        tools: Optional[List] = None,
        model: Optional[Any] = None
    ):
        """
        Initialize the AWS consultant agent.
        
        Args:
            system_prompt: The system prompt for the agent
            tools: List of MCP tools available to the agent
            model: Optional model instance (None for Anthropic, OllamaModel for local)
        """
        if not system_prompt or not system_prompt.strip():
            raise ValueError("system_prompt cannot be empty")
        
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model = model
        self._agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """
        Create the underlying Strands agent instance.
        
        Returns:
            Configured Agent instance with Claude via Bedrock or Ollama and MCP tools
        """
        agent_config = {
            'system_prompt': self.system_prompt,
        }
        
        if self.model is not None:
            agent_config['model'] = self.model
        
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
        model_info = (
            f"model={self.model.__class__.__name__}"
            if self.model else "model=Anthropic"
        )
        return f"AWSConsultantAgent({model_info}, tools={len(self.tools)})"
    
    def __str__(self) -> str:
        """Return user-friendly string representation."""
        model_name = (
            self.model.__class__.__name__
            if self.model else "Anthropic"
        )
        return f"AWS Consultant Agent ({model_name}) with {len(self.tools)} MCP tool(s)"
