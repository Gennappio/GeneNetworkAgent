"""
LangGraph Definition - Main workflow graph for Gene Network Quality Agent
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict
import os

# Import node functions
from .nodes.load_model import load_model_node
from .nodes.topology import topology_node
from .nodes.dynamics import dynamics_node
from .nodes.perturb import perturb_node
from .nodes.validate import validate_node
from .nodes.controller import controller_node
from .nodes.report import report_node


class AgentState(TypedDict):
    """State shared between all nodes in the graph."""
    # Input
    model_path: str
    max_iterations: int
    
    # Analysis results
    model: Dict[str, Any]
    topology: Dict[str, Any]
    dynamics: Dict[str, Any]
    perturb: Dict[str, Any]
    validate: Dict[str, Any]
    
    # Control flow
    iterations: int
    should_continue: bool
    stop_reason: str
    loop_reason: str
    
    # Output
    report: Dict[str, Any]
    report_path: str
    
    # Error handling
    error: str


def create_quality_agent_graph() -> StateGraph:
    """
    Create the main LangGraph workflow for gene network quality analysis.
    """
    print("🔧 Creating Gene Network Quality Agent graph...")
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("load_model", load_model_node)
    workflow.add_node("topology", topology_node)
    workflow.add_node("dynamics", dynamics_node)
    workflow.add_node("perturb", perturb_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("controller", controller_node)
    workflow.add_node("report", report_node)
    
    # Define the flow
    workflow.set_entry_point("load_model")
    
    # Linear analysis flow
    workflow.add_edge("load_model", "topology")
    workflow.add_edge("topology", "dynamics")
    workflow.add_edge("dynamics", "perturb")
    workflow.add_edge("perturb", "validate")
    workflow.add_edge("validate", "controller")
    
    # Controller decision point
    workflow.add_conditional_edges(
        "controller",
        should_continue_analysis,
        {
            "continue": "topology",  # Loop back to topology analysis
            "stop": "report"         # Generate final report
        }
    )
    
    # End after report
    workflow.add_edge("report", END)
    
    print("✅ Graph created successfully")
    return workflow


def should_continue_analysis(state: AgentState) -> str:
    """
    Conditional edge function to determine if analysis should continue.
    """
    should_continue = state.get("should_continue", False)
    
    if should_continue:
        print("🔄 Controller decision: CONTINUE iteration")
        return "continue"
    else:
        print("⏹️  Controller decision: STOP and generate report")
        return "stop"


def run_quality_analysis(model_path: str, max_iterations: int = 3) -> Dict[str, Any]:
    """
    Run the complete gene network quality analysis.
    
    Args:
        model_path: Path to the gene network model file (YAML or BND)
        max_iterations: Maximum number of analysis iterations
    
    Returns:
        Final state with all analysis results
    """
    print(f"🚀 Starting Gene Network Quality Analysis")
    print(f"   Model: {model_path}")
    print(f"   Max iterations: {max_iterations}")
    print("="*60)
    
    # Create the graph
    workflow = create_quality_agent_graph()
    app = workflow.compile()
    
    # Initialize state
    initial_state = {
        "model_path": model_path,
        "max_iterations": max_iterations,
        "iterations": 0,
        "should_continue": True,
        "model": {},
        "topology": {},
        "dynamics": {},
        "perturb": {},
        "validate": {},
        "stop_reason": "",
        "loop_reason": "",
        "report": {},
        "report_path": "",
        "error": ""
    }
    
    try:
        # Run the workflow
        print("🔄 Executing analysis workflow...")
        final_state = app.invoke(initial_state)
        
        print("="*60)
        print("✅ Analysis completed successfully!")
        
        # Print summary
        print_analysis_summary(final_state)
        
        return final_state
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return {**initial_state, "error": str(e)}


def print_analysis_summary(state: Dict[str, Any]):
    """
    Print a summary of the analysis results.
    """
    print("\n📊 ANALYSIS SUMMARY")
    print("="*40)
    
    # Basic info
    model = state.get("model", {})
    print(f"Network: {model.get('name', 'Unknown')}")
    print(f"Iterations: {state.get('iterations', 0)}")
    print(f"Stop reason: {state.get('stop_reason', 'unknown')}")
    
    # Quality scores
    validate = state.get("validate", {})
    if validate and not validate.get("error"):
        score = validate.get("plausibility_score", 0.0)
        issues = len(validate.get("issues", []))
        print(f"Biological plausibility: {score:.2f}")
        print(f"Issues found: {issues}")
    
    # Dynamics
    dynamics = state.get("dynamics", {})
    if dynamics and not dynamics.get("error"):
        unstable = len(dynamics.get("unstable_nodes", []))
        oscillations = dynamics.get("has_oscillations", False)
        print(f"Unstable nodes: {unstable}")
        print(f"Oscillations: {'Yes' if oscillations else 'No'}")
    
    # Perturbations
    perturb = state.get("perturb", {})
    if perturb and not perturb.get("error"):
        robust = len(perturb.get("robust_nodes", []))
        sensitive = len(perturb.get("sensitive_nodes", []))
        print(f"Robust nodes: {robust}")
        print(f"Sensitive nodes: {sensitive}")
    
    # Report location
    report_path = state.get("report_path", "")
    if report_path:
        print(f"Report saved: {report_path}")


# Convenience function for CLI usage
def main():
    """
    Main function for CLI usage.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Gene Network Quality Agent')
    parser.add_argument('model_path', help='Path to gene network model file')
    parser.add_argument('--max-iterations', type=int, default=3, 
                       help='Maximum number of analysis iterations')
    
    args = parser.parse_args()
    
    # Check if model file exists
    if not os.path.exists(args.model_path):
        print(f"❌ Error: Model file not found: {args.model_path}")
        return
    
    # Run analysis
    result = run_quality_analysis(args.model_path, args.max_iterations)
    
    # Check for errors
    if result.get("error"):
        print(f"❌ Analysis failed: {result['error']}")
        return
    
    print("\n🎉 Analysis completed successfully!")


if __name__ == "__main__":
    main()
