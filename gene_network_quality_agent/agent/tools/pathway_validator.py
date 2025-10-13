"""
Pathway Validator Tool
Specialized biological pathway validation
Demonstrates MCP-style tool with specific biological knowledge
"""
from typing import Dict, Any, List, Set


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate specific biological pathways in the network
    """
    model_data = state.get("model_data")
    if not model_data:
        raise ValueError("model_data not found in state")
    
    print("🔄 Validating biological pathways...")
    
    results = validate_known_pathways(model_data)
    
    print(f"✅ Pathway validation complete:")
    print(f"   Pathways found: {len(results['detected_pathways'])}")
    print(f"   Pathway score: {results['pathway_score']:.2f}")
    print(f"   Missing pathways: {len(results['missing_pathways'])}")
    
    return {
        "pathway_validation_results": results,
        "biology_deep_validated": True
    }


def validate_known_pathways(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate presence and correctness of known biological pathways
    """
    nodes = model_data["nodes"]
    node_names = set(nodes.keys())
    
    # Define known pathway patterns
    pathway_patterns = {
        "p53_pathway": {
            "required_nodes": ["p53", "DNA_damage", "Apoptosis"],
            "optional_nodes": ["MDM2", "p21", "ATM"],
            "expected_logic": {
                "p53": ["DNA_damage"],
                "Apoptosis": ["p53"],
                "MDM2": ["p53"],
                "p21": ["p53"]
            }
        },
        "cell_cycle": {
            "required_nodes": ["p21", "Growth_Arrest"],
            "optional_nodes": ["Proliferation", "Growth_factors"],
            "expected_logic": {
                "Growth_Arrest": ["p21"],
                "Proliferation": ["Growth_factors"]
            }
        },
        "apoptosis_pathway": {
            "required_nodes": ["Apoptosis"],
            "optional_nodes": ["BCL2", "p53", "Necrosis"],
            "expected_logic": {
                "Apoptosis": ["p53"],
                "BCL2": ["Growth_factors"]
            }
        },
        "mapk_pathway": {
            "required_nodes": ["ERK", "MEK1_2"],
            "optional_nodes": ["RAF", "RAS", "JNK", "p38"],
            "expected_logic": {
                "ERK": ["MEK1_2"],
                "MEK1_2": ["RAF"],
                "RAF": ["RAS"]
            }
        },
        "pi3k_akt_pathway": {
            "required_nodes": ["AKT", "PI3K"],
            "optional_nodes": ["PTEN", "PDK1", "p70"],
            "expected_logic": {
                "AKT": ["PI3K"],
                "p70": ["AKT"]
            }
        }
    }
    
    detected_pathways = []
    missing_pathways = []
    pathway_scores = []
    
    for pathway_name, pattern in pathway_patterns.items():
        score = validate_pathway_pattern(nodes, node_names, pattern)
        
        if score > 0.3:  # Threshold for pathway detection
            detected_pathways.append({
                "name": pathway_name,
                "score": score,
                "completeness": calculate_pathway_completeness(node_names, pattern)
            })
        else:
            missing_pathways.append({
                "name": pathway_name,
                "score": score,
                "missing_nodes": find_missing_nodes(node_names, pattern)
            })
        
        pathway_scores.append(score)
    
    # Calculate overall pathway score
    overall_score = sum(pathway_scores) / len(pathway_scores) if pathway_scores else 0.0
    
    # Generate recommendations
    recommendations = generate_pathway_recommendations(detected_pathways, missing_pathways)
    
    return {
        "detected_pathways": detected_pathways,
        "missing_pathways": missing_pathways,
        "pathway_score": overall_score,
        "recommendations": recommendations,
        "pathway_analysis": {
            "total_pathways_checked": len(pathway_patterns),
            "pathways_detected": len(detected_pathways),
            "pathways_missing": len(missing_pathways)
        }
    }


def validate_pathway_pattern(nodes: Dict[str, Any], node_names: Set[str], pattern: Dict[str, Any]) -> float:
    """
    Validate a specific pathway pattern and return a score (0.0 to 1.0)
    """
    score = 0.0
    max_score = 0.0
    
    # Check required nodes
    required_nodes = pattern["required_nodes"]
    max_score += len(required_nodes) * 2  # Required nodes worth more
    
    for node in required_nodes:
        if any(node.lower() in name.lower() for name in node_names):
            score += 2
    
    # Check optional nodes
    optional_nodes = pattern.get("optional_nodes", [])
    max_score += len(optional_nodes)
    
    for node in optional_nodes:
        if any(node.lower() in name.lower() for name in node_names):
            score += 1
    
    # Check logic relationships (simplified)
    expected_logic = pattern.get("expected_logic", {})
    max_score += len(expected_logic) * 1.5
    
    for target_node, source_nodes in expected_logic.items():
        # Find matching nodes in the network
        target_matches = [name for name in node_names if target_node.lower() in name.lower()]
        
        if target_matches:
            target_name = target_matches[0]
            target_info = nodes.get(target_name, {})
            logic = target_info.get("logic", "")
            
            # Check if any source nodes are mentioned in the logic
            for source_node in source_nodes:
                if any(source_node.lower() in name.lower() for name in node_names):
                    source_matches = [name for name in node_names if source_node.lower() in name.lower()]
                    if source_matches and any(source_match in logic for source_match in source_matches):
                        score += 1.5
    
    return score / max_score if max_score > 0 else 0.0


def calculate_pathway_completeness(node_names: Set[str], pattern: Dict[str, Any]) -> float:
    """Calculate what percentage of pathway components are present"""
    required_nodes = pattern["required_nodes"]
    optional_nodes = pattern.get("optional_nodes", [])
    all_nodes = required_nodes + optional_nodes
    
    present_count = 0
    for node in all_nodes:
        if any(node.lower() in name.lower() for name in node_names):
            present_count += 1
    
    return present_count / len(all_nodes) if all_nodes else 0.0


def find_missing_nodes(node_names: Set[str], pattern: Dict[str, Any]) -> List[str]:
    """Find which nodes are missing from a pathway pattern"""
    required_nodes = pattern["required_nodes"]
    missing = []
    
    for node in required_nodes:
        if not any(node.lower() in name.lower() for name in node_names):
            missing.append(node)
    
    return missing


def generate_pathway_recommendations(detected_pathways: List[Dict], missing_pathways: List[Dict]) -> List[str]:
    """Generate recommendations based on pathway analysis"""
    recommendations = []
    
    # Recommendations for missing pathways
    for pathway in missing_pathways:
        if pathway["score"] < 0.1:  # Completely missing
            recommendations.append(f"Consider adding {pathway['name']} components: {', '.join(pathway['missing_nodes'])}")
        else:  # Partially present
            recommendations.append(f"Complete {pathway['name']} by adding: {', '.join(pathway['missing_nodes'])}")
    
    # Recommendations for incomplete detected pathways
    for pathway in detected_pathways:
        if pathway["completeness"] < 0.7:
            recommendations.append(f"Enhance {pathway['name']} completeness (currently {pathway['completeness']:.1%})")
    
    # General recommendations
    if len(detected_pathways) < 2:
        recommendations.append("Network lacks diversity - consider adding more biological pathways")
    
    if not any("p53" in p["name"] for p in detected_pathways):
        recommendations.append("Add DNA damage response pathway (p53-mediated)")
    
    return recommendations


# Tool definition for the registry
TOOL_DEFINITION = {
    "name": "pathway_validator",
    "description": "Validate specific biological pathways and their completeness",
    "function_name": "execute",
    "input_requirements": ["model_data"],
    "output_provides": ["pathway_validation_results", "biology_deep_validated"],
    "category": "validator",
    "priority": 75,
    "enabled": True
}
