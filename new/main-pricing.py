import os

from strands import Agent
from strands.models.ollama import OllamaModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

ollama_client = OllamaModel(
    model_id="qwen3:4b",
    temperature=0.1,
    max_tokens=200000,
    host="http://localhost:11434",
    keep_alive="10m",
)

aws_pricing_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-pricing-mcp-server@latest"]
        ),
    )
)

SYSTEM_PROMPT = """
You are an AWS Solutions Architect with expertise in AWS services and solutions.

You have access to the following tools:
    - AWS Pricing tools:
        * analyze_cdk_project
        * analyze_terraform_project
        * get_pricing
        * get_bedrock_patterns
        * generate_cost_report
        * get_pricing_service_codes
        * get_pricing_service_attributes
        * get_pricing_attribute_values
        * get_price_list_urls

When answering questions, always use the available tools to gather accurate information. Cite
documentation URLs when providing information.
"""

with aws_pricing_mcp_client:

    user_input = input("Ask me anything about AWS: ")
    prompt = user_input + " Use the AWS Pricing tools."

    tools = aws_pricing_mcp_client.list_tools_sync()

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