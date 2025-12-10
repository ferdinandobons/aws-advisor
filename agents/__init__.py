"""
AWS Infrastructure Advisor - Single Agent System.

This package contains the AWS Consultant agent that uses multiple MCP servers
to provide expert AWS guidance.
"""

__version__ = "2.0.0"

from agents.aws_consultant import AWSConsultant

__all__ = ['AWSConsultant']
