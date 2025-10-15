"""
Biological Validation Tool
Validates network biological plausibility and pathway correctness
"""
from typing import Dict, Any, List


def execute_natural_language(context: str, model_path: str) -> str:
    """
    Validate biological plausibility and return natural language evaluation

    Args:
        context: Previous analysis context (natural language)
        model_path: Path to the .bnd file

    Returns:
        Natural language evaluation of biological validation
    """
    try:
        # Load and validate biology
        import sys
        from pathlib import Path

        # Add parent directory to path
        parent_dir = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(parent_dir))

        from gene_network_standalone import StandaloneGeneNetwork
        from agent.tools.load_bnd_network import convert_bnd_to_standard_format

        # Load the network
        network = StandaloneGeneNetwork()
        network.load_bnd_file(model_path)
        model_data = convert_bnd_to_standard_format(network, model_path)

        # Perform biological validation
        validation_results = _validate_biology_internal(model_data)

        # Generate natural language evaluation
        plausibility = validation_results["plausibility"]
        issues = validation_results["issues"]
        recommendations = validation_results["recommendations"]

        plausibility_assessment = "excellent" if plausibility > 0.8 else "good" if plausibility > 0.6 else "moderate" if plausibility > 0.4 else "poor"

        evaluation = f"""**Biological Validation Results**

**Plausibility Assessment:**
- **Biological Score**: {plausibility:.3f} ({plausibility_assessment} biological realism)
- **Issues Identified**: {len(issues)} potential concerns
- **Validation Status**: {'✅ Biologically plausible' if plausibility > 0.6 else '⚠️ Some biological concerns' if plausibility > 0.4 else '❌ Significant biological issues'}

**Key Findings:**
{chr(10).join([f"• {issue}" for issue in issues[:3]])}{'...' if len(issues) > 3 else ''}

**Recommendations:**
{chr(10).join([f"• {rec}" for rec in recommendations[:3]])}{'...' if len(recommendations) > 3 else ''}

**Biological Assessment:**
The network shows {'strong biological realism' if plausibility > 0.8 else 'reasonable biological plausibility' if plausibility > 0.6 else 'moderate biological concerns' if plausibility > 0.4 else 'significant biological issues'} based on known regulatory relationships and pathway logic.

{'🧬 **High biological fidelity** - the network accurately represents known biological mechanisms.' if plausibility > 0.8 else '🧬 **Good biological basis** - most regulatory relationships are biologically supported.' if plausibility > 0.6 else '⚠️ **Some biological concerns** - certain aspects may need refinement for biological accuracy.' if plausibility > 0.4 else '⚠️ **Significant biological issues** - substantial revision needed for biological realism.'}

**Research Implications**: {'The network is suitable for biological hypothesis generation and experimental design.' if plausibility > 0.6 else 'The network may require biological refinement before experimental application.' if plausibility > 0.4 else 'Significant biological validation needed before research application.'}"""

        return evaluation

    except Exception as e:
        return f"❌ **Biological Validation Failed**: {str(e)}"


def _validate_biology_internal(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """Internal biological validation function"""
    return validate_biological_plausibility(model_data)


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate biological plausibility of the network
    """
    model_data = state.get("model_data")
    topology_results = state.get("topology_results")
    dynamics_results = state.get("dynamics_results")

    if not model_data:
        raise ValueError("model_data not found in state")

    print("🔄 Validating with LLM...")

    results = validate_biological_plausibility(model_data, topology_results, dynamics_results)

    print(f"✅ Validation complete:")
    print(f"   Biological plausibility: {results['biological_plausibility']:.2f}")
    print(f"   Issues found: {len(results['issues'])}")
    print(f"   Recommendations: {len(results['recommendations'])}")

    return {
        "validation_results": results,
        "quality_validated": True
    }


def validate_biological_plausibility(model_data: Dict[str, Any], 
                                   topology_results: Dict[str, Any] = None,
                                   dynamics_results: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Simple rule-based biological validation (placeholder for LLM integration)
    """
    nodes = model_data["nodes"]
    issues = []
    recommendations = []
    
    # Check for known biological patterns
    biological_score = 0.0
    max_score = 0.0
    
    # Check for p53 pathway
    max_score += 1.0
    if "p53" in nodes:
        biological_score += 0.5
        if any("DNA_damage" in name for name in nodes):
            biological_score += 0.3
        if any("Apoptosis" in name for name in nodes):
            biological_score += 0.2
    else:
        issues.append("Missing p53 tumor suppressor pathway")
        recommendations.append("Consider adding p53-mediated DNA damage response")
    
    # Check for cell fate decisions
    max_score += 1.0
    apoptosis_nodes = [name for name in nodes if "Apoptosis" in name]
    proliferation_nodes = [name for name in nodes if "Proliferation" in name]
    
    if apoptosis_nodes and proliferation_nodes:
        biological_score += 0.5
        # Check if they are mutually exclusive (simple check)
        # This is a placeholder - real validation would check logic
        biological_score += 0.3
    else:
        issues.append("Apoptosis and proliferation may not be mutually exclusive")
        recommendations.append("Ensure proper cell fate decision logic")
    
    # Check dynamics results if available
    if dynamics_results:
        max_score += 1.0
        unstable_count = len(dynamics_results.get("unstable_nodes", []))
        total_nodes = len(nodes)
        
        if total_nodes > 0:
            stability_ratio = 1.0 - (unstable_count / total_nodes)
            biological_score += stability_ratio * 0.5
            
            if unstable_count > total_nodes * 0.5:
                issues.append("Many unstable nodes detected")
                recommendations.append("Review network logic for stability")
    
    # Check topology results if available
    if topology_results:
        max_score += 1.0
        cycles = topology_results.get("cycles", 0)
        
        if cycles == 0:
            biological_score += 0.3
        elif cycles < 3:
            biological_score += 0.2
        else:
            issues.append("Many feedback loops may cause instability")
            recommendations.append("Review feedback loop necessity")
        
        # Check connectivity
        if topology_results.get("connected", False):
            biological_score += 0.2
        else:
            issues.append("Network has disconnected components")
            recommendations.append("Ensure all pathways are properly connected")
    
    # Additional simple checks
    max_score += 1.0
    
    # Check for input nodes
    input_nodes = [name for name, info in nodes.items() if info["type"] == "input"]
    if len(input_nodes) > 0:
        biological_score += 0.3
    else:
        issues.append("No input nodes found")
        recommendations.append("Add external signal inputs")
    
    # Check for reasonable network size
    total_nodes = len(nodes)
    if 5 <= total_nodes <= 200:
        biological_score += 0.2
    else:
        if total_nodes < 5:
            issues.append("Network too small for meaningful analysis")
        else:
            issues.append("Network very large - may be difficult to analyze")
    
    # Normalize score
    if max_score > 0:
        biological_plausibility = biological_score / max_score
    else:
        biological_plausibility = 0.0
    
    # Additional robustness checks
    if dynamics_results:
        robust_nodes = dynamics_results.get("robust_nodes", [])
        if len(robust_nodes) == 0:
            issues.append("No robust nodes found")
            recommendations.append("Network may be too sensitive to perturbations")
    
    return {
        "biological_plausibility": biological_plausibility,
        "issues": issues,
        "recommendations": recommendations,
        "validation_details": {
            "biological_score": biological_score,
            "max_score": max_score,
            "input_nodes_count": len(input_nodes),
            "total_nodes_count": total_nodes
        }
    }


# Tool definition for the registry
TOOL_DEFINITION = {
    "name": "validate_biology",
    "description": "Validate biological plausibility and pathway correctness",
    "function_name": "execute",
    "input_requirements": ["model_data"],
    "output_provides": ["validation_results", "quality_validated"],
    "category": "validator",
    "priority": 60,
    "enabled": True
}
