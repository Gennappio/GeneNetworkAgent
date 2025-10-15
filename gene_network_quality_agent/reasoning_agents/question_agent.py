#!/usr/bin/env python3
"""
Question Agent - Answers specific questions about analysis reports
"""

import os
import logging
from pathlib import Path

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback

logger = logging.getLogger(__name__)

def execute_natural_language(report_content: str, question: str, model_path: str = None) -> str:
    """
    Answer specific question about the natural language report with automatic tool execution

    Args:
        report_content: The analysis report content
        question: The specific question to answer
        model_path: Path to the model file for tool execution

    Returns:
        Complete answer including executed tool results
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
    from .tool_executor import discover_available_tools, extract_tool_recommendations, execute_recommended_tools

    # Dynamically discover available tools
    available_tools_dict = discover_available_tools()
    available_tools = [
        f"{tool_info['display_name']} - {tool_info['definition']['description']}"
        for tool_info in available_tools_dict.values()
    ]

    prompt = f"""You are an expert in gene network analysis. Please answer the following question based on the analysis report provided.

Available analysis tools:
{chr(10).join([f"- {tool}" for tool in available_tools])}

Question: {question}

Analysis Report:
{report_content}

Please provide a detailed, accurate answer based on the information in the report. If the report doesn't contain enough information to answer the question, please state that clearly and suggest what additional analysis might be needed.

If running specific analysis tools would help answer the question better, mention which tools should be executed and why.

Respond in clear, natural language suitable for researchers."""

    try:
        # Use simple chain without complex parsing
        result = llm.invoke([{"role": "user", "content": prompt}])

        # Parse response to extract tool recommendations
        response_text = result.content
        recommended_tools = extract_tool_recommendations(response_text, available_tools_dict)

        # Execute recommended tools if model_path is available
        if recommended_tools and model_path:
            logger.info(f"Question agent executing recommended tools: {recommended_tools}")
            additional_analysis = execute_recommended_tools(model_path, recommended_tools)
            if additional_analysis:
                response_text += f"\n\n## Additional Analysis Results\n{additional_analysis}"
        elif recommended_tools:
            logger.info(f"Question agent identified tools to run: {recommended_tools}, but no model path provided")

        return response_text
    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        return f"Error processing question: {e}"



# Tool definition for dynamic discovery
TOOL_DEFINITION = {
    "name": "question_agent",
    "description": "Answers specific questions about gene network analysis reports",
    "function_name": "execute_natural_language",
    "input_requirements": ["report_content", "question"],
    "output_provides": ["answer", "recommended_tools"],
    "category": "reasoning",
    "priority": 25,  # Medium priority - used for Q&A
    "enabled": True
}
