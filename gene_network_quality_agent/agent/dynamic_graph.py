"""
Dynamic LangGraph - Adaptive analysis workflow using tool registry
"""
import importlib.util
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from agent.tool_registry import tool_registry
from agent.dynamic_controller import DynamicController, dynamic_controller_node


class DynamicAnalysisState:
    """State for dynamic analysis workflow"""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def update(self, other):
        if isinstance(other, dict):
            self.data.update(other)
        else:
            self.data.update(other.data)
    
    def keys(self):
        return self.data.keys()
    
    def items(self):
        return self.data.items()
    
    def values(self):
        return self.data.values()


def create_dynamic_tool_node(tool_name: str):
    """
    Create a LangGraph node function for a specific tool
    """
    def tool_node(state: Dict[str, Any]) -> Dict[str, Any]:
        controller = state.get("controller")
        if not controller:
            controller = DynamicController()
            state["controller"] = controller
        
        # Execute the tool step
        result = controller.execute_pipeline_step(tool_name, state)
        return result
    
    return tool_node


def create_dynamic_graph() -> StateGraph:
    """
    Create a dynamic LangGraph that adapts based on available tools
    """
    print("🔧 Creating dynamic Gene Network Quality Agent graph...")
    
    # Discover available tools
    tool_registry.discover_tools()
    
    # Create the graph
    graph = StateGraph(dict)
    
    # Add tool nodes dynamically
    for tool_name, tool_def in tool_registry.tools.items():
        node_func = create_dynamic_tool_node(tool_name)
        graph.add_node(tool_name, node_func)
        print(f"   Added node: {tool_name}")
    
    # Add controller node
    graph.add_node("controller", dynamic_controller_node)
    print("   Added node: controller")
    
    # Add pipeline executor node
    graph.add_node("pipeline_executor", pipeline_executor_node)
    print("   Added node: pipeline_executor")
    
    # Set entry point
    graph.set_entry_point("pipeline_executor")

    # Pipeline executor runs first, then controller decides what to do next
    graph.add_edge("pipeline_executor", "controller")

    # Add conditional edges from controller
    graph.add_conditional_edges(
        "controller",
        controller_decision,
        {
            "CONTINUE": "pipeline_executor",
            "STOP": END
        }
    )
    
    print("✅ Dynamic graph created successfully")
    return graph.compile()


def pipeline_executor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the current pipeline step by step
    """
    controller = state.get("controller")
    if not controller:
        controller = DynamicController()
        state["controller"] = controller
    
    # Get or create initial pipeline
    if not controller.current_pipeline:
        available_data = list(state.keys())
        controller.current_pipeline = controller.create_initial_pipeline(available_data)
    
    # Check if we have a next pipeline from controller decision
    controller_decision = state.get("controller_decision", {})
    if "next_pipeline" in controller_decision:
        controller.current_pipeline = controller_decision["next_pipeline"]
        print(f"🔄 Using adapted pipeline: {' → '.join(controller.current_pipeline)}")
    
    # Execute all steps in current pipeline
    for step in controller.current_pipeline:
        print(f"🔄 Executing pipeline step: {step}")
        state = controller.execute_pipeline_step(step, state)
    
    return state


def controller_decision(state: Dict[str, Any]) -> str:
    """
    Determine next action based on controller decision
    """
    decision = state.get("controller_decision", {})

    # If no controller decision exists yet (first iteration), continue with analysis
    if not decision:
        print("🎯 Controller decision: CONTINUE (first iteration)")
        return "CONTINUE"

    action = decision.get("action", "STOP")

    print(f"🎯 Controller decision: {action}")
    return action


def run_dynamic_analysis(model_path: str, max_iterations: int = 3, verbose: bool = False) -> Dict[str, Any]:
    """
    Run dynamic analysis using the tool registry system
    """
    print("🚀 Starting Dynamic Gene Network Quality Analysis")
    print(f"   Model: {model_path}")
    print(f"   Max iterations: {max_iterations}")
    print("=" * 60)
    
    # Create dynamic graph
    graph = create_dynamic_graph()
    
    # Initialize state
    initial_state = {
        "model_path": model_path,
        "max_iterations": max_iterations,
        "verbose": verbose,
        "iteration": 0
    }
    
    # Execute the graph
    print("🔄 Executing dynamic analysis workflow...")
    final_state = graph.invoke(initial_state)
    
    print("=" * 60)
    print("✅ Dynamic analysis completed successfully!")
    
    return final_state


# Example of how to add a new tool at runtime
def add_custom_tool_example():
    """
    Example of how to add a custom tool at runtime
    """
    from agent.tool_registry import ToolDefinition
    
    def custom_analysis(state: Dict[str, Any]) -> Dict[str, Any]:
        print("🔄 Running custom analysis...")
        # Custom analysis logic here
        return {
            "custom_results": {"analysis": "completed"},
            "custom_analyzed": True
        }
    
    custom_tool = ToolDefinition(
        name="custom_analysis",
        description="Custom analysis tool added at runtime",
        function=custom_analysis,
        input_requirements=["model_data"],
        output_provides=["custom_results", "custom_analyzed"],
        category="analyzer",
        priority=75,
        enabled=True
    )
    
    tool_registry.register_tool(custom_tool)
    print("✅ Custom tool registered successfully!")


if __name__ == "__main__":
    # Example usage
    result = run_dynamic_analysis("models/simple_good_network.bnd", max_iterations=2, verbose=True)
    print(f"Final result keys: {list(result.keys())}")
