import os

from strands import Agent
from strands.models.ollama import OllamaModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

ollama_client = OllamaModel(
    model_id="llama3.2:3b",
    temperature=0.1,
    max_tokens=200000,
    host="http://localhost:11434",
    keep_alive="10m",
)

aws_docs_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-documentation-mcp-server@latest"]
        ),
    )
)

aws_billing_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.billing-cost-management-mcp-server@latest"],
            env={
                "AWS_PROFILE": "default",
                "AWS_REGION": "eu-central-1",
                "FASTMCP_LOG_LEVEL": "ERROR"
            }
        )
    )
)

SYSTEM_PROMPT = """
You are an AWS Solutions Architect with expertise in AWS services and solutions.

You have access to the following tools:
    - AWS Billing tools:
        * cost-explorer
        * compute-optimizer
        * cost-optimization
        * storage-lens
        * aws-pricing
        * bcm-pricing-calc
        * budgets
        * cost-anomaly
        * cost-comparison
        * free-tier-usage
        * rec-details
        * ri-performance
        * sp-performance
        * session-sql

When answering questions, always use the available tools to gather accurate information. Cite
documentation URLs when providing information.
"""

with aws_billing_mcp_client:

    user_input = input("Ask me anything about AWS: ")
    prompt = user_input + " Use the AWS Billing tools."

    tools = aws_billing_mcp_client.list_tools_sync()

    print(f"Available tools from MCP servers ({len(tools)}):")
    for tool in tools:
        print(f"- {tool.tool_name}")

    aws_agent = Agent(
        model=ollama_client,
        system_prompt=SYSTEM_PROMPT,
        tools=[tools],
    )

    aws_agent(prompt)

# Get the event loop metrics summary
metrics_summary = aws_agent.event_loop_metrics.get_summary()

# Print token usage
print("Token Usage:")
print(f"  Input tokens:  {metrics_summary['accumulated_usage']['inputTokens']:,}")
print(f"  Output tokens: {metrics_summary['accumulated_usage']['outputTokens']:,}")
print(f"  Total tokens:  {metrics_summary['accumulated_usage']['totalTokens']:,}")

# Print tool metrics
print("\nTool Usage:")

for tool_name, tool_data in metrics_summary['tool_usage'].items():
    stats = tool_data['execution_stats']
    print(f"  {tool_name}:")
    print(f"    Calls: {stats['call_count']} (Success: {stats['success_count']}, Error: {stats['error_count']})")
    print(f"    Success rate: {stats['success_rate'] * 100:.1f}%")