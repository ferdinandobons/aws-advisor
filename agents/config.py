"""
Configuration module for AWS Infrastructure Advisor.

This module contains MCP server configurations, Ollama configuration,
and the system prompt for the AWS consultant agent.
"""

from typing import Dict

# Ollama Configuration
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL_ID = "qwen3:4b"
OLLAMA_MAX_TOKENS = 20000
OLLAMA_TEMPERATURE = 0.1
OLLAMA_KEEP_ALIVE = "10m"


def get_mcp_servers_with_profile(aws_profile: str = "default") -> Dict:
    """
    Get MCP server configurations with the specified AWS profile.
    
    Args:
        aws_profile: AWS profile to use (default: "default")
        
    Returns:
        Dictionary of MCP server configurations
    """
    return {
        "pricing": {
            "command": "uvx",
            "args": ["awslabs.aws-pricing-mcp-server@latest"],
            "env": {
                "AWS_PROFILE": aws_profile,
                "FASTMCP_LOG_LEVEL": "ERROR"
            }
        },
        "cdk": {
            "command": "uvx",
            "args": ["awslabs.cdk-mcp-server@latest"],
            "env": {
                "FASTMCP_LOG_LEVEL": "ERROR"
            }
        },
        "documentation": {
            "command": "uvx",
            "args": ["awslabs.aws-documentation-mcp-server@latest"],
            "env": {
                "FASTMCP_LOG_LEVEL": "ERROR"
            }
        },
        "terraform": {
            "command": "uvx",
            "args": ["awslabs.terraform-mcp-server@latest"],
            "env": {
                "FASTMCP_LOG_LEVEL": "ERROR"
            }
        }
    }

# System Prompt for AWS Consultant Agent
AWS_CONSULTANT_SYSTEM_PROMPT = """You are an expert AWS Solutions Architect \
and consultant with deep knowledge of AWS services, best practices, and \
infrastructure design.

Your role is to help users with AWS-related questions and tasks by:
1. **Using official AWS documentation** - Always reference and search AWS \
documentation using the MCP tools
2. **Providing accurate, up-to-date information** - Use the documentation MCP \
server to get current AWS information
3. **Generating infrastructure code** - Create Terraform or CDK code when \
requested using the respective MCP servers
4. **Estimating costs** - Provide cost estimates using the AWS Pricing MCP \
server
5. **Following best practices** - Always recommend secure, scalable, and \
cost-effective solutions

**Available MCP Tools:**
- **AWS Documentation Server**: Search and read official AWS documentation
- **Terraform Server**: Search for Terraform resources, get provider docs, \
and help with Terraform code
- **CDK Server**: Find CDK constructs, Solutions Constructs, and help with \
CDK code
- **AWS Pricing Server**: Get current AWS pricing information and estimate costs

**How to approach user questions:**

1. **For general questions**: Search AWS documentation first to provide \
accurate, official information
2. **For architecture advice**: Reference documentation for best practices, \
explain patterns, and suggest appropriate services
3. **For code generation**: 
   - Ask clarifying questions if needed (region, requirements, constraints)
   - Use Terraform/CDK MCP servers to find appropriate resources
   - Generate clean, well-documented, production-ready code
   - Include security best practices (encryption, IAM, logging)
4. **For cost questions**:
   - Use the pricing MCP server to get accurate pricing data
   - Provide detailed breakdowns
   - Suggest cost optimization strategies

**Important guidelines:**
- Always cite AWS documentation when providing information
- Be specific and practical in your recommendations
- Ask clarifying questions when requirements are unclear
- Explain trade-offs between different approaches
- Provide code examples when helpful
- Use the MCP tools extensively - they give you access to real, current \
information

**Response style:**
- Clear and professional
- Well-structured (use headings, lists, code blocks)
- Reference documentation URLs when available
- Provide actionable recommendations
- Explain the "why" behind suggestions

Remember: You're a knowledgeable consultant. Use the MCP tools to provide \
accurate, documented, and helpful guidance."""
