"""
Tool Registry - Dynamic tool discovery and management system
Supports MCP-style tool registration and runtime discovery
"""
import os
import importlib
import importlib.util
import inspect
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ToolDefinition:
    """Definition of an analysis tool"""
    name: str
    description: str
    function: Callable
    input_requirements: List[str]
    output_provides: List[str]
    category: str
    priority: int = 50  # Higher = more important
    enabled: bool = True


class ToolRegistry:
    """
    Dynamic tool registry that discovers and manages analysis tools
    """
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.categories = {
            "loader": "Data loading and parsing tools",
            "analyzer": "Network analysis tools", 
            "validator": "Validation and quality assessment tools",
            "reporter": "Report generation tools",
            "controller": "Control flow and decision tools"
        }
    
    def register_tool(self, tool_def: ToolDefinition):
        """Register a new tool"""
        print(f"📝 Registering tool: {tool_def.name} ({tool_def.category})")
        self.tools[tool_def.name] = tool_def
    
    def discover_tools(self, tools_dir: str = "agent/tools"):
        """
        Discover tools from directory structure
        Each tool should have a .py file with:
        - A function with the tool logic
        - A TOOL_DEFINITION dict with metadata
        """
        tools_path = Path(tools_dir)
        if not tools_path.exists():
            print(f"⚠️  Tools directory not found: {tools_dir}")
            return
        
        print(f"🔍 Discovering tools in {tools_dir}...")
        
        for tool_file in tools_path.glob("*.py"):
            if tool_file.name.startswith("__"):
                continue
                
            try:
                # Import the tool module
                module_name = f"agent.tools.{tool_file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, tool_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for TOOL_DEFINITION
                if hasattr(module, 'TOOL_DEFINITION'):
                    tool_def_dict = module.TOOL_DEFINITION
                    
                    # Find the main function (should match tool name or be called 'execute')
                    func_name = tool_def_dict.get('function_name', 'execute')
                    if hasattr(module, func_name):
                        func = getattr(module, func_name)
                        
                        tool_def = ToolDefinition(
                            name=tool_def_dict['name'],
                            description=tool_def_dict['description'],
                            function=func,
                            input_requirements=tool_def_dict.get('input_requirements', []),
                            output_provides=tool_def_dict.get('output_provides', []),
                            category=tool_def_dict.get('category', 'analyzer'),
                            priority=tool_def_dict.get('priority', 50),
                            enabled=tool_def_dict.get('enabled', True)
                        )
                        
                        self.register_tool(tool_def)
                    else:
                        print(f"⚠️  Tool {tool_file.name}: function '{func_name}' not found")
                else:
                    print(f"⚠️  Tool {tool_file.name}: TOOL_DEFINITION not found")
                    
            except Exception as e:
                print(f"❌ Error loading tool {tool_file.name}: {e}")
    
    def get_tools_by_category(self, category: str) -> List[ToolDefinition]:
        """Get all tools in a category, sorted by priority"""
        tools = [tool for tool in self.tools.values() 
                if tool.category == category and tool.enabled]
        return sorted(tools, key=lambda t: t.priority, reverse=True)
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a specific tool by name"""
        return self.tools.get(name)
    
    def find_tools_for_requirements(self, requirements: List[str]) -> List[ToolDefinition]:
        """Find tools that can provide the required outputs"""
        matching_tools = []
        for tool in self.tools.values():
            if tool.enabled and any(req in tool.output_provides for req in requirements):
                matching_tools.append(tool)
        return sorted(matching_tools, key=lambda t: t.priority, reverse=True)
    
    def can_execute_tool(self, tool_name: str, available_data: List[str]) -> bool:
        """Check if a tool can be executed with available data"""
        tool = self.get_tool(tool_name)
        if not tool or not tool.enabled:
            return False
        
        # Check if all input requirements are met
        return all(req in available_data for req in tool.input_requirements)
    
    def list_tools(self) -> Dict[str, List[str]]:
        """List all tools by category"""
        result = {}
        for category in self.categories:
            tools = self.get_tools_by_category(category)
            result[category] = [f"{t.name}: {t.description}" for t in tools]
        return result
    
    def get_execution_plan(self, goals: List[str], available_data: List[str]) -> List[str]:
        """
        Create an execution plan to achieve goals with available data
        This is a simple dependency resolver
        """
        plan = []
        current_data = available_data.copy()
        remaining_goals = goals.copy()
        
        max_iterations = 20  # Prevent infinite loops
        iteration = 0
        
        while remaining_goals and iteration < max_iterations:
            iteration += 1
            progress_made = False
            
            # Find tools that can help achieve remaining goals
            for goal in remaining_goals.copy():
                tools = self.find_tools_for_requirements([goal])
                
                for tool in tools:
                    if self.can_execute_tool(tool.name, current_data):
                        plan.append(tool.name)
                        current_data.extend(tool.output_provides)
                        remaining_goals.remove(goal)
                        progress_made = True
                        break
                
                if goal not in remaining_goals:  # Goal was achieved
                    break
            
            if not progress_made:
                print(f"⚠️  Cannot achieve remaining goals: {remaining_goals}")
                break
        
        return plan


# Global registry instance
tool_registry = ToolRegistry()
