#!/usr/bin/env python3
"""
Summary Agent - Generates focused biologist-friendly summaries
"""

import os
import logging

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback

logger = logging.getLogger(__name__)

def execute_natural_language(report_content: str, focus: str) -> str:
    """
    Generate focused biologist-friendly summary from natural language report
    
    Args:
        report_content: The analysis report content
        focus: The focus area for the summary
        
    Returns:
        Focused summary text
    """
    
    # Initialize LLM
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        return "Error: OPENAI_API_KEY not set"
    
    llm = ChatOpenAI(
        api_key=openai_api_key,
        model="gpt-3.5-turbo",
        temperature=0.1,
        max_tokens=2000
    )

    prompt = f"""You are an expert biologist and researcher. Please create a focused summary of this gene network analysis report with emphasis on: {focus}

Analysis Report:
{report_content}

Create a comprehensive, publication-ready summary that:
1. Highlights key findings relevant to {focus}
2. Explains biological significance and implications
3. Identifies potential therapeutic targets or research directions
4. Uses language appropriate for biological researchers
5. Focuses specifically on aspects related to {focus}

Format the summary in clear sections with markdown formatting."""

    try:
        # Use simple chain without complex parsing
        result = llm.invoke([{"role": "user", "content": prompt}])
        return result.content
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return f"Error generating summary: {e}"

# Tool definition for dynamic discovery
TOOL_DEFINITION = {
    "name": "summary_agent",
    "description": "Generates focused biologist-friendly summaries of analysis reports",
    "function_name": "execute_natural_language",
    "input_requirements": ["report_content", "focus"],
    "output_provides": ["focused_summary"],
    "category": "reasoning",
    "priority": 15,  # Lower priority - used for final summaries
    "enabled": True
}
