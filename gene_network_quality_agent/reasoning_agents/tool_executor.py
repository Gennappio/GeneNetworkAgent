#!/usr/bin/env python3
"""
Tool Executor - Shared utility for reasoning agents to execute recommended tools
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def discover_available_tools() -> dict:
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

def extract_tool_recommendations(response_text: str, available_tools_dict: dict) -> list:
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

def execute_recommended_tools(model_path: str, recommended_tools: list) -> str:
    """Execute recommended tools and return results"""
    if not recommended_tools:
        return ""
    
    logger.info(f"Executing recommended tools: {', '.join(recommended_tools)}")
    
    # Get available tools dynamically
    available_tools_dict = discover_available_tools()
    
    # Create mapping from display names to modules
    tool_modules = {}
    for tool_name, tool_info in available_tools_dict.items():
        display_name = tool_info['display_name']
        tool_modules[display_name] = tool_info['module']
    
    results = []
    context = f"Analyzing gene network: {model_path}"
    
    for tool_name in recommended_tools:
        if tool_name in tool_modules:
            try:
                module_name = tool_modules[tool_name]
                module_parts = module_name.split('.')
                module = __import__(module_name, fromlist=[module_parts[-1]])
                result = module.execute_natural_language(context, model_path)
                results.append(f"## {tool_name}\n{result}\n")
                context += f"\n\nPrevious analysis from {tool_name}:\n{result}"
            except Exception as e:
                logger.error(f"Failed to execute {tool_name}: {e}")
                results.append(f"## {tool_name}\nFailed to execute: {e}\n")
        else:
            logger.warning(f"Tool not found: {tool_name}. Available tools: {list(tool_modules.keys())}")
    
    return "\n".join(results)

def extract_model_path_from_report(report_path: str) -> str:
    """Extract model path from report content"""
    try:
        with open(report_path, 'r') as f:
            content = f.read()

        # Look for model path patterns in the report
        import re
        import os

        # Pattern 1: Look for "Network:" lines with .bnd files
        lines = content.split('\n')
        for line in lines:
            if '**Network:**' in line:
                # Extract filename from the line
                parts = line.split('**Network:**')
                if len(parts) > 1:
                    filename = parts[1].strip()
                    # Try different path combinations
                    possible_paths = [
                        f"models/{filename}",
                        filename,
                        f"../models/{filename}",
                        f"models/{filename}.bnd" if not filename.endswith('.bnd') else f"models/{filename}",
                        f"{filename}.bnd" if not filename.endswith('.bnd') else filename
                    ]

                    for path in possible_paths:
                        if os.path.exists(path):
                            return path

        # Pattern 2: Look for any .bnd file mentions
        bnd_pattern = r'(\S+\.bnd)'
        matches = re.findall(bnd_pattern, content)
        if matches:
            for match in matches:
                # Try different path combinations
                possible_paths = [
                    f"models/{match}",
                    match,
                    f"../models/{match}"
                ]

                for path in possible_paths:
                    if os.path.exists(path):
                        return path

        return None
    except Exception as e:
        logger.error(f"Failed to extract model path from report: {e}")
        return None
