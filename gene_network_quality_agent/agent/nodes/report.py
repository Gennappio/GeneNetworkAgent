"""
Report Generation Node - Creates comprehensive analysis report
"""
import yaml
import os
from datetime import datetime
from typing import Dict, Any, List


def report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate final report.
    Simple implementation for debugging.
    """
    print("🔄 Generating report...")
    
    try:
        # Generate comprehensive report
        report_data = generate_comprehensive_report(state)
        
        # Save report to file
        report_path = save_report(report_data)
        
        print(f"✅ Report generated:")
        print(f"   File: {report_path}")
        print(f"   Iterations: {report_data['summary']['total_iterations']}")
        print(f"   Final quality: {report_data['summary']['final_quality_score']:.2f}")
        
        state["report"] = report_data
        state["report_path"] = report_path
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        state["report"] = {"error": str(e)}
    
    return state


def generate_comprehensive_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comprehensive analysis report.
    """
    
    # Extract data from state
    model = state.get("model", {})
    topology = state.get("topology", {})
    dynamics = state.get("dynamics", {})
    perturb = state.get("perturb", {})
    validate = state.get("validate", {})
    
    iterations = state.get("iterations", 0)
    stop_reason = state.get("stop_reason", "unknown")
    loop_reason = state.get("loop_reason", "")
    
    # Calculate final quality score
    final_quality = calculate_final_quality_score(state)
    
    # Generate report structure
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "gene_network_quality_agent_version": "1.0.0",
            "analysis_type": "iterative_quality_assessment"
        },
        
        "summary": {
            "network_name": model.get("name", "Unknown Network"),
            "network_description": model.get("description", "No description"),
            "total_iterations": iterations,
            "stop_reason": stop_reason,
            "loop_reason": loop_reason,
            "final_quality_score": final_quality,
            "analysis_status": "completed" if not any(
                data.get("error") for data in [topology, dynamics, perturb, validate]
            ) else "completed_with_errors"
        },
        
        "network_structure": generate_structure_summary(model, topology),
        "dynamics_analysis": generate_dynamics_summary(dynamics),
        "perturbation_analysis": generate_perturbation_summary(perturb),
        "biological_validation": generate_validation_summary(validate),
        "recommendations": generate_recommendations(state),
        "detailed_results": {
            "topology": topology,
            "dynamics": dynamics,
            "perturbation": perturb,
            "validation": validate
        }
    }
    
    return report


def calculate_final_quality_score(state: Dict[str, Any]) -> float:
    """
    Calculate final quality score from all analyses.
    """
    scores = []
    
    # Validation score
    validate = state.get("validate", {})
    if validate and not validate.get("error"):
        scores.append(validate.get("plausibility_score", 0.0))
    
    # Dynamics stability score
    dynamics = state.get("dynamics", {})
    if dynamics and not dynamics.get("error"):
        unstable_count = len(dynamics.get("unstable_nodes", []))
        has_oscillations = dynamics.get("has_oscillations", False)
        
        stability_score = 1.0 - min(0.5, unstable_count * 0.1)
        if has_oscillations:
            stability_score -= 0.2
        
        scores.append(max(0.0, stability_score))
    
    # Topology score
    topology = state.get("topology", {})
    if topology and not topology.get("error"):
        is_connected = topology.get("is_connected", False)
        cycle_count = len(topology.get("cycles", []))
        
        topo_score = 0.8 if is_connected else 0.4
        if cycle_count > 10:
            topo_score -= 0.3
        
        scores.append(max(0.0, topo_score))
    
    return sum(scores) / len(scores) if scores else 0.0


def generate_structure_summary(model: Dict[str, Any], topology: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate network structure summary.
    """
    nodes = model.get("nodes", {})
    
    structure = {
        "total_nodes": len(nodes),
        "input_nodes": len([n for n in nodes.values() if n.get("type") == "input"]),
        "logic_nodes": len([n for n in nodes.values() if n.get("type") == "logic"]),
        "node_list": list(nodes.keys())
    }
    
    if topology and not topology.get("error"):
        structure.update({
            "total_edges": topology.get("edge_count", 0),
            "network_density": topology.get("density", 0.0),
            "is_connected": topology.get("is_connected", False),
            "feedback_loops": len(topology.get("cycles", [])),
            "strongly_connected_components": topology.get("scc_count", 0)
        })
    
    return structure


def generate_dynamics_summary(dynamics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate dynamics analysis summary.
    """
    if dynamics.get("error"):
        return {"status": "error", "message": dynamics["error"]}
    
    return {
        "status": "completed",
        "attractors_found": len(dynamics.get("attractors", [])),
        "unstable_nodes": dynamics.get("unstable_nodes", []),
        "unstable_node_count": len(dynamics.get("unstable_nodes", [])),
        "has_oscillations": dynamics.get("has_oscillations", False),
        "simulations_run": dynamics.get("num_simulations", 0),
        "stability_assessment": "stable" if len(dynamics.get("unstable_nodes", [])) < 3 else "unstable"
    }


def generate_perturbation_summary(perturb: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate perturbation analysis summary.
    """
    if perturb.get("error"):
        return {"status": "error", "message": perturb["error"]}
    
    return {
        "status": "completed",
        "nodes_tested": perturb.get("total_nodes_tested", 0),
        "robust_nodes": perturb.get("robust_nodes", []),
        "sensitive_nodes": perturb.get("sensitive_nodes", []),
        "knockout_tests": len(perturb.get("knockouts", [])),
        "overexpression_tests": len(perturb.get("overexpressions", [])),
        "robustness_assessment": "robust" if len(perturb.get("robust_nodes", [])) > 0 else "sensitive"
    }


def generate_validation_summary(validate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate biological validation summary.
    """
    if validate.get("error"):
        return {"status": "error", "message": validate["error"]}
    
    return {
        "status": "completed",
        "plausibility_score": validate.get("plausibility_score", 0.0),
        "issues_found": len(validate.get("issues", [])),
        "issues": validate.get("issues", []),
        "recommendations_count": len(validate.get("recommendations", [])),
        "recommendations": validate.get("recommendations", []),
        "biological_patterns": validate.get("biological_patterns", {}),
        "validation_method": validate.get("validation_method", "unknown")
    }


def generate_recommendations(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate actionable recommendations.
    """
    recommendations = []
    
    # Validation recommendations
    validate = state.get("validate", {})
    if validate and not validate.get("error"):
        for rec in validate.get("recommendations", []):
            recommendations.append({
                "category": "biological_validation",
                "priority": "high",
                "description": rec,
                "source": "LLM_validation"
            })
    
    # Dynamics recommendations
    dynamics = state.get("dynamics", {})
    if dynamics and not dynamics.get("error"):
        unstable_nodes = dynamics.get("unstable_nodes", [])
        if unstable_nodes:
            recommendations.append({
                "category": "network_stability",
                "priority": "medium",
                "description": f"Review stability of nodes: {', '.join(unstable_nodes[:5])}",
                "source": "dynamics_analysis"
            })
        
        if dynamics.get("has_oscillations"):
            recommendations.append({
                "category": "network_dynamics",
                "priority": "medium",
                "description": "Investigate oscillatory behavior and consider dampening mechanisms",
                "source": "dynamics_analysis"
            })
    
    # Topology recommendations
    topology = state.get("topology", {})
    if topology and not topology.get("error"):
        cycles = topology.get("cycles", [])
        if len(cycles) > 10:
            recommendations.append({
                "category": "network_topology",
                "priority": "low",
                "description": f"Consider reducing feedback loops (currently {len(cycles)})",
                "source": "topology_analysis"
            })
    
    return recommendations


def save_report(report_data: Dict[str, Any]) -> str:
    """
    Save report to YAML file.
    """
    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_iterative_{timestamp}.yaml"
    filepath = os.path.join(reports_dir, filename)
    
    # Save report
    with open(filepath, 'w') as f:
        yaml.dump(report_data, f, default_flow_style=False, indent=2)
    
    return filepath
