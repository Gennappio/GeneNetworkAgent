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

def execute_natural_language(report_content: str, question: str) -> tuple[str, list]:
    """
    Answer specific question about the natural language report
    
    Args:
        report_content: The analysis report content
        question: The specific question to answer
        
    Returns:
        Tuple of (answer_text, recommended_tools)
    """
    
    # Initialize LLM
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        return "Error: OPENAI_API_KEY not set", []
    
    llm = ChatOpenAI(
        api_key=openai_api_key,
        model="gpt-3.5-turbo",
        temperature=0.1,
        max_tokens=2000
    )
    
    # Dynamically discover available tools
    available_tools_dict = _discover_available_tools()
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
        recommended_tools = _extract_tool_recommendations(response_text, available_tools_dict)
        
        return response_text, recommended_tools
    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        return f"Error processing question: {e}", []

def _discover_available_tools() -> dict:
    """Dynamically discover all available tools from the tools directory"""
    tools = {}
    tools_dir = Path("agent/tools")
    
    if not tools_dir.exists():
        logger.warning(f"Tools directory not found: {tools_dir}")
        return tools
    
    for tool_file in tools_dir.glob("*.py"):
        if tool_file.name.startswith("__"):
            continue
            
        try:
            # Import the module dynamically
            module_name = f"agent.tools.{tool_file.stem}"
            module_parts = module_name.split('.')
            module = __import__(module_name, fromlist=[module_parts[-1]])
            
            # Check if it has TOOL_DEFINITION
            if hasattr(module, 'TOOL_DEFINITION'):
                tool_def = module.TOOL_DEFINITION
                if tool_def.get('enabled', True):  # Only include enabled tools
                    tools[tool_def['name']] = {
                        'definition': tool_def,
                        'module': module_name,
                        'display_name': tool_def['name'].replace('_', ' ').title()
                    }
                    
        except Exception as e:
            logger.warning(f"Failed to load tool {tool_file}: {e}")
    
    return tools

def _extract_tool_recommendations(response_text: str, available_tools_dict: dict) -> list:
    """Extract tool recommendations from LLM response using dynamic tool discovery"""
    recommended_tools = []
    
    response_lower = response_text.lower()
    
    # Check for tool mentions by name and description keywords
    for tool_name, tool_info in available_tools_dict.items():
        tool_def = tool_info['definition']
        display_name = tool_info['display_name']
        
        # Check for direct tool name mentions
        if tool_name.lower() in response_lower or display_name.lower() in response_lower:
            if any(trigger in response_lower for trigger in ["should be run", "recommend", "suggest", "execute", "run"]):
                recommended_tools.append(display_name)
                continue
        
        # Check for description-based keywords
        description = tool_def.get('description', '').lower()
        description_words = description.split()
        
        # If multiple description words are mentioned, consider it a recommendation
        matches = sum(1 for word in description_words if len(word) > 3 and word in response_lower)
        if matches >= 2 and any(trigger in response_lower for trigger in ["should be run", "recommend", "suggest", "execute", "run"]):
            recommended_tools.append(display_name)
    
    return list(set(recommended_tools))  # Remove duplicates

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
