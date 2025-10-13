"""
Report Generation Tool
Creates comprehensive analysis reports in YAML format
"""
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comprehensive analysis report
    """
    print("🔄 Generating report...")
    
    # Create report data
    report_data = create_report_data(state)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"reports/report_iterative_{timestamp}.yaml"
    
    # Ensure reports directory exists
    Path("reports").mkdir(exist_ok=True)
    
    with open(report_filename, 'w') as f:
        yaml.dump(report_data, f, default_flow_style=False, indent=2)
    
    # Calculate final quality score
    final_quality = calculate_final_quality(state)
    
    print(f"✅ Report generated:")
    print(f"   File: {report_filename}")
    print(f"   Iterations: {state.get('iteration', 1)}")
    print(f"   Final quality: {final_quality:.2f}")
    
    return {
        "report_file": report_filename,
        "report_data": report_data,
        "final_quality": final_quality,
        "report_generated": True
    }


def create_report_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create comprehensive report data from analysis state
    """
    model_data = state.get("model_data", {})
    topology_results = state.get("topology_results", {})
    dynamics_results = state.get("dynamics_results", {})
    perturbation_results = state.get("perturbation_results", {})
    validation_results = state.get("validation_results", {})
    controller = state.get("controller")
    
    # Get execution summary
    execution_summary = {}
    if controller:
        execution_summary = controller.get_execution_summary()
    
    report = {
        "analysis_metadata": {
            "timestamp": datetime.now().isoformat(),
            "network_name": model_data.get("name", "Unknown"),
            "network_description": model_data.get("description", ""),
            "total_iterations": state.get("iteration", 1),
            "stop_reason": state.get("controller_decision", {}).get("reason", "unknown")
        },
        
        "network_summary": {
            "total_nodes": len(model_data.get("nodes", {})),
            "input_nodes": len([n for n in model_data.get("nodes", {}).values() if n.get("type") == "input"]),
            "logic_nodes": len([n for n in model_data.get("nodes", {}).values() if n.get("type") == "logic"])
        },
        
        "topology_analysis": topology_results,
        "dynamics_analysis": dynamics_results,
        "perturbation_analysis": perturbation_results,
        "biological_validation": validation_results,
        "execution_summary": execution_summary,
        
        "final_assessment": {
            "biological_plausibility": validation_results.get("biological_plausibility", 0.0),
            "total_issues": len(validation_results.get("issues", [])),
            "total_recommendations": len(validation_results.get("recommendations", [])),
            "quality_score": calculate_final_quality(state)
        }
    }
    
    return report


def calculate_final_quality(state: Dict[str, Any]) -> float:
    """
    Calculate overall quality score from all analyses
    """
    scores = []
    
    # Biological validation score
    validation_results = state.get("validation_results", {})
    if validation_results:
        scores.append(validation_results.get("biological_plausibility", 0.0))
    
    # Topology score (based on connectivity and reasonable complexity)
    topology_results = state.get("topology_results", {})
    if topology_results:
        # Simple topology scoring
        connected = topology_results.get("connected", False)
        cycles = topology_results.get("cycles", 0)
        nodes = topology_results.get("nodes", 0)
        
        topology_score = 0.0
        if connected:
            topology_score += 0.5
        if 0 <= cycles <= 3:  # Reasonable number of cycles
            topology_score += 0.3
        if 5 <= nodes <= 100:  # Reasonable network size
            topology_score += 0.2
        
        scores.append(topology_score)
    
    # Dynamics score (based on stability)
    dynamics_results = state.get("dynamics_results", {})
    if dynamics_results:
        unstable_count = len(dynamics_results.get("unstable_nodes", []))
        total_nodes = len(state.get("model_data", {}).get("nodes", {}))
        
        if total_nodes > 0:
            stability_ratio = 1.0 - (unstable_count / total_nodes)
            scores.append(max(0.0, stability_ratio))
    
    # Return average score
    return sum(scores) / len(scores) if scores else 0.0


# Tool definition for the registry
TOOL_DEFINITION = {
    "name": "generate_report",
    "description": "Generate comprehensive analysis report in YAML format",
    "function_name": "execute", 
    "input_requirements": ["model_data"],
    "output_provides": ["report_file", "report_data", "final_quality", "report_generated"],
    "category": "reporter",
    "priority": 10,  # Low priority - usually done last
    "enabled": True
}
