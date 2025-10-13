"""
Validation Node - Validates biological pathways using LLM one-shot
"""
from typing import Dict, Any, List
import os


def validate_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate network using LLM.
    Simple implementation for debugging.
    """
    print("🔄 Validating with LLM...")
    
    model = state.get("model")
    topology = state.get("topology")
    dynamics = state.get("dynamics")
    perturb = state.get("perturb")
    
    if not model:
        print("❌ No model to validate")
        state["validate"] = {"error": "No model available"}
        return state
    
    try:
        # Simple validation (placeholder for LLM integration)
        validation_result = perform_biological_validation(model, topology, dynamics, perturb)
        
        print(f"✅ Validation complete:")
        print(f"   Biological plausibility: {validation_result['plausibility_score']:.2f}")
        print(f"   Issues found: {len(validation_result['issues'])}")
        print(f"   Recommendations: {len(validation_result['recommendations'])}")
        
        state["validate"] = validation_result
        
    except Exception as e:
        print(f"❌ Error in validation: {e}")
        state["validate"] = {"error": str(e)}
    
    return state


def perform_biological_validation(model: Dict[str, Any], topology: Dict[str, Any], 
                                 dynamics: Dict[str, Any], perturb: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple biological validation (placeholder for LLM).
    In full implementation, this would call an LLM with biological knowledge.
    """
    
    # Placeholder validation logic
    issues = []
    recommendations = []
    plausibility_score = 0.8  # Default score
    
    # Check basic biological principles
    nodes = model.get("nodes", {})
    
    # Check for common biological patterns
    has_p53 = "p53" in nodes
    has_apoptosis = "Apoptosis" in nodes
    has_proliferation = "Proliferation" in nodes
    
    if has_p53 and has_apoptosis:
        plausibility_score += 0.1
    else:
        issues.append("Missing p53-apoptosis pathway")
        recommendations.append("Consider adding p53-mediated apoptosis pathway")
    
    if has_apoptosis and has_proliferation:
        # Check if they are mutually exclusive
        apoptosis_logic = nodes.get("Apoptosis", {}).get("logic", "")
        proliferation_logic = nodes.get("Proliferation", {}).get("logic", "")
        
        if "!Proliferation" in apoptosis_logic or "!Apoptosis" in proliferation_logic:
            plausibility_score += 0.1
        else:
            issues.append("Apoptosis and proliferation may not be mutually exclusive")
            recommendations.append("Consider making apoptosis and proliferation mutually exclusive")
    
    # Check topology issues
    if topology and not topology.get("error"):
        cycles = topology.get("cycles", [])
        if len(cycles) > 5:
            issues.append(f"Many feedback loops detected ({len(cycles)})")
            recommendations.append("Review feedback loops for biological relevance")
            plausibility_score -= 0.1
    
    # Check dynamics issues
    if dynamics and not dynamics.get("error"):
        unstable_nodes = dynamics.get("unstable_nodes", [])
        if len(unstable_nodes) > len(nodes) * 0.3:
            issues.append("Many unstable nodes detected")
            recommendations.append("Review network stability")
            plausibility_score -= 0.1
    
    # Check perturbation results
    if perturb and not perturb.get("error"):
        robust_nodes = perturb.get("robust_nodes", [])
        sensitive_nodes = perturb.get("sensitive_nodes", [])
        
        if len(robust_nodes) == 0:
            issues.append("No robust nodes found")
            recommendations.append("Network may be too sensitive to perturbations")
            plausibility_score -= 0.1
    
    # Ensure score is between 0 and 1
    plausibility_score = max(0.0, min(1.0, plausibility_score))
    
    return {
        "plausibility_score": plausibility_score,
        "issues": issues,
        "recommendations": recommendations,
        "biological_patterns": {
            "has_p53_pathway": has_p53 and has_apoptosis,
            "has_cell_fate_decisions": has_apoptosis and has_proliferation,
            "pathway_count": count_known_pathways(nodes)
        },
        "validation_method": "rule_based_placeholder"
    }


def count_known_pathways(nodes: Dict[str, Any]) -> int:
    """
    Count known biological pathways in the network.
    """
    pathway_count = 0
    
    # p53 pathway
    if "p53" in nodes and "MDM2" in nodes:
        pathway_count += 1
    
    # Apoptosis pathway
    if "Apoptosis" in nodes and any(gene in nodes for gene in ["BCL2", "BAX", "p53"]):
        pathway_count += 1
    
    # Cell cycle pathway
    if any(gene in nodes for gene in ["Proliferation", "Rb", "E2F", "Cyclin"]):
        pathway_count += 1
    
    # DNA damage response
    if "DNA_damage" in nodes and "p53" in nodes:
        pathway_count += 1
    
    return pathway_count


def generate_llm_prompt(model: Dict[str, Any], topology: Dict[str, Any], 
                       dynamics: Dict[str, Any], perturb: Dict[str, Any]) -> str:
    """
    Generate prompt for LLM validation (for future implementation).
    """
    prompt = f"""
Please analyze this gene regulatory network for biological plausibility:

Network: {model.get('name', 'Unknown')}
Description: {model.get('description', 'No description')}

Nodes ({len(model.get('nodes', {}))}):
"""
    
    nodes = model.get("nodes", {})
    for node_name, node_data in nodes.items():
        node_type = node_data.get("type", "unknown")
        logic = node_data.get("logic", "")
        prompt += f"- {node_name} ({node_type}): {logic}\n"
    
    if topology and not topology.get("error"):
        prompt += f"\nTopology Analysis:\n"
        prompt += f"- Cycles: {len(topology.get('cycles', []))}\n"
        prompt += f"- Connected: {topology.get('is_connected', False)}\n"
    
    if dynamics and not dynamics.get("error"):
        prompt += f"\nDynamics Analysis:\n"
        prompt += f"- Attractors: {len(dynamics.get('attractors', []))}\n"
        prompt += f"- Unstable nodes: {dynamics.get('unstable_nodes', [])}\n"
    
    prompt += """
Please evaluate:
1. Biological plausibility (0-1 score)
2. Known pathway violations
3. Recommendations for improvement
4. Missing important interactions

Respond in JSON format with: plausibility_score, issues, recommendations
"""
    
    return prompt
