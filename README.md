# AWS Infrastructure Advisor

☁️ **AI-powered AWS consultant** using official documentation and real-time data to provide expert AWS guidance.

## Overview

Single-agent system powered by Claude (Anthropic) or Ollama (local models) that acts as your personal AWS Solutions Architect.

**Key Features:**
- 💬 Interactive consultation with an AWS expert
- 📚 Always references official AWS documentation
- 🔧 Generates Terraform and CDK code
- 💰 Real-time AWS pricing data
- 🖥️ Option to run locally with Ollama models

## Prerequisites

### 1. AWS Profile
Configure your AWS credentials and profile. Uses your default AWS profile, or specify one with `--aws-profile`.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) For Local Model Support
To use local Ollama models instead of Claude via AWS Bedrock:

1. Install Ollama: https://ollama.ai
2. Pull the model: `ollama pull qwen2.5:3b`
3. Start Ollama: `ollama serve`

## Quick Start

### Interactive Mode
```bash
# Using Claude via AWS Bedrock (default)
python main.py

# Using local Ollama model
python main.py --local
```

### Single Query
```bash
# Using Claude via AWS Bedrock (default)
python main.py "How do I set up a serverless REST API?"

# Using local Ollama model
python main.py --local "How do I set up a serverless REST API?"
```

### With Custom AWS Profile
```bash
python main.py --aws-profile my-profile "Get pricing for EC2 t3.medium"

# Combining local model with custom AWS profile
python main.py --local --aws-profile my-profile "Get pricing for EC2 t3.medium"
```

## Usage Examples

**Architecture guidance:**
```bash
python main.py "Best way to build a real-time data pipeline?"

# With local model
python main.py --local "Best way to build a real-time data pipeline?"
```

**Code generation:**
```bash
python main.py "Generate Terraform code for a secure S3 bucket"
```

**Cost estimation:**
```bash
python main.py "Cost to run DynamoDB with 10GB and 100 RCU/WCU?"
```

**Best practices:**
```bash
python main.py "Security best practices for Lambda functions?"
```

## What You Get

1. **Documentation-backed answers** - Cites official AWS docs
2. **Architecture guidance** - Service recommendations and patterns
3. **Production-ready code** - Secure Terraform or CDK code
4. **Cost estimates** - Real-time pricing with breakdowns
5. **Best practices** - Security, performance, and optimization tips

## Architecture

```
AWSConsultant (Claude via Bedrock or Ollama Local Model)
    ├─→ AWS Documentation MCP Server
    ├─→ Terraform MCP Server
    ├─→ AWS CDK MCP Server
    └─→ AWS Pricing MCP Server
```

### Model Options
- **Claude via AWS Bedrock** (default): Cloud-based, requires AWS credentials
- **Ollama (qwen2.5:3b)** (with `--local` flag): Local inference, no cloud dependencies for the LLM

## Project Structure

```
aws-advisor/
├── main.py                    # Main application
├── agents/
│   ├── config.py              # MCP server configs
│   ├── base.py                # Base agent class
│   └── aws_consultant.py      # Main consultant agent
├── outputs/                    # Saved consultations
├── requirements.txt           # Python dependencies
└── README.md
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **AWS credentials not configured** | Run `aws configure` or set AWS profile |
| **Import errors** | `pip install -r requirements.txt` |
| **MCP server timeout** | First run takes 30-60 seconds |
| **Connection errors** | Check internet connection |
| **Ollama model not found** | Run `ollama pull qwen2.5:3b` |
| **Ollama connection failed** | Start Ollama with `ollama serve` |

---

**Built with:** Strands Agents • Claude / Ollama • AWS MCP Servers • Model Context Protocol