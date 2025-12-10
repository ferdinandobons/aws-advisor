"""
AWS Consultant Agent.

This is the main agent that acts as an AWS consultant using
all available MCP servers.
"""

from typing import List
from agents.base import AWSConsultantAgent
from agents.config import AWS_CONSULTANT_SYSTEM_PROMPT


class AWSConsultant(AWSConsultantAgent):
    """
    General AWS consultant agent with access to all MCP tools.
    
    This agent can:
    - Answer AWS questions using official documentation
    - Provide architecture guidance
    - Generate Terraform code
    - Generate CDK code
    - Estimate infrastructure costs
    - Recommend best practices
    
    It uses Claude via AWS Bedrock with access to 4 MCP servers:
    - AWS Documentation
    - Terraform Registry
    - AWS CDK
    - AWS Pricing
    """
    
    def __init__(self, all_tools: List):
        """
        Initialize the AWS consultant.
        
        Args:
            all_tools: Combined list of tools from all MCP servers
        """
        super().__init__(
            system_prompt=AWS_CONSULTANT_SYSTEM_PROMPT,
            tools=all_tools
        )
    
    def consult(self, user_request: str) -> str:
        """
        Consult with the user on their AWS needs.
        
        Args:
            user_request: The user's question, requirement, or request
            
        Returns:
            Comprehensive response with recommendations, code, costs, etc.
        """
        return self.ask(user_request)

