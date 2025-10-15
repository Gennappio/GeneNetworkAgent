#!/usr/bin/env python3
"""
Refinement Agent - Provides analysis refinement suggestions
"""

import os
import logging
from pathlib import Path

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback

logger = logging.getLogger(__name__)

def execute_natural_language(report_content: str, context: str = "", model_path: str = None) -> str:
    """
    Analyze report and provide refinement suggestions with automatic tool execution

    Args:
        report_content: The analysis report content
        context: Additional context (unused for this agent)
        model_path: Path to the model file for tool execution

    Returns:
        Complete refinement analysis including executed tool results
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

    # Import tool execution utilities
    from .tool_executor import discover_available_tools, extract_tool_recommendations, execute_recommended_tools, extract_model_path_from_report

    # Dynamically discover available tools
    available_tools_dict = discover_available_tools()
    available_tools = [
        f"{tool_info['display_name']} - {tool_info['definition']['description']}"
        for tool_info in available_tools_dict.values()
    ]

    # Create prompt for refinement suggestions
    prompt = f"""You are an expert in gene network analysis. Please review this analysis report and provide suggestions for improvement or additional insights.

Available analysis tools:
{chr(10).join([f"- {tool}" for tool in available_tools])}

Report to review:
{report_content}

Please provide:
1. Key strengths of the current analysis
2. Areas that could be improved or expanded
3. Specific suggestions for additional analysis
4. Any potential concerns or limitations
5. If additional tool execution would be helpful, specify which tools should be run and why

Respond in clear, natural language suitable for researchers."""

    try:
        # Use simple chain without complex parsing
        result = llm.invoke([{"role": "user", "content": prompt}])

        # Parse response to extract tool recommendations
        response_text = result.content
        recommended_tools = extract_tool_recommendations(response_text, available_tools_dict)

        # Execute recommended tools if model_path is available
        if recommended_tools and model_path:
            logger.info(f"Refinement agent executing recommended tools: {recommended_tools}")
            additional_analysis = execute_recommended_tools(model_path, recommended_tools)
            if additional_analysis:
                response_text += f"\n\n## Additional Analysis Results\n{additional_analysis}"
        elif recommended_tools:
            logger.info(f"Refinement agent identified tools to run: {recommended_tools}, but no model path provided")

        return response_text
    except Exception as e:
        logger.error(f"Refinement suggestions failed: {e}")
        return f"Error generating refinement suggestions: {e}"



# Tool definition for dynamic discovery
TOOL_DEFINITION = {
    "name": "refinement_agent",
    "description": "Provides analysis refinement suggestions and identifies gaps in current analysis",
    "function_name": "execute_natural_language",
    "input_requirements": ["report_content"],
    "output_provides": ["refinement_suggestions", "recommended_tools"],
    "category": "reasoning",
    "priority": 20,  # Medium priority - used for refinement
    "enabled": True
}
