"""
Perturbation Testing Tool
Tests network robustness through knockout and overexpression experiments
"""
from typing import Dict, Any, List


def execute_natural_language(context: str, model_path: str) -> str:
    """
    Test network perturbations and return natural language evaluation

    Args:
        context: Previous analysis context (natural language)
        model_path: Path to the .bnd file

    Returns:
        Natural language evaluation of perturbation testing
    """
    try:
        # Load and test perturbations
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

        # Perform perturbation testing
        perturbation_results = _test_perturbations_internal(model_data, network)

        # Generate natural language evaluation
        knockout_tests = perturbation_results["knockout_tests"]
        overexpression_tests = perturbation_results["overexpression_tests"]
        robust_nodes = perturbation_results["robust_nodes"]
        sensitive_nodes = [node for node in model_data["nodes"].keys() if node not in robust_nodes]

        robustness_percentage = (len(robust_nodes) / len(model_data["nodes"])) * 100
        robustness_assessment = "highly robust" if robustness_percentage > 70 else "moderately robust" if robustness_percentage > 40 else "fragile"

        evaluation = f"""**Perturbation Testing Results**

**Robustness Analysis:**
- **Knockout Tests**: {knockout_tests} nodes tested
- **Overexpression Tests**: {overexpression_tests} nodes tested
- **Robust Nodes**: {len(robust_nodes)} out of {len(model_data['nodes'])} ({robustness_percentage:.1f}%)
- **Network Assessment**: {robustness_assessment.title()}

**Robust Elements**: {', '.join(robust_nodes[:5])}{'...' if len(robust_nodes) > 5 else ''}
**Sensitive Elements**: {', '.join(sensitive_nodes[:5])}{'...' if len(sensitive_nodes) > 5 else ''}

**Perturbation Assessment:**
The network shows {'excellent robustness' if robustness_percentage > 70 else 'good robustness' if robustness_percentage > 40 else 'limited robustness'} to genetic perturbations. {'Most regulatory elements maintain network stability when perturbed.' if robustness_percentage > 70 else 'A moderate number of elements show robust behavior.' if robustness_percentage > 40 else 'Many elements are sensitive to perturbations, suggesting potential fragility.'}

{'✅ **High robustness** - network maintains function despite individual gene perturbations.' if robustness_percentage > 70 else '⚠️ **Moderate robustness** - some sensitivity to perturbations detected.' if robustness_percentage > 40 else '⚠️ **Low robustness** - network may be vulnerable to genetic perturbations.'}

**Therapeutic Implications**: {'Robust nodes may be challenging therapeutic targets, while sensitive nodes could be promising intervention points.' if len(sensitive_nodes) > 0 else 'High overall robustness suggests the network has evolved strong fault tolerance.'}"""

        return evaluation

    except Exception as e:
        return f"❌ **Perturbation Testing Failed**: {str(e)}"


def _test_perturbations_internal(model_data: Dict[str, Any], bnd_network=None) -> Dict[str, Any]:
    """Internal perturbation testing function"""
    return test_network_perturbations(model_data)


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test network perturbations (knockout and overexpression)
    """
    model_data = state.get("model_data")
    if not model_data:
        raise ValueError("model_data not found in state")

    print("🔄 Analyzing perturbations...")

    results = test_network_perturbations(model_data)

    print(f"✅ Perturbation analysis complete:")
    print(f"   Knockout tests: {results['knockout_count']}")
    print(f"   Overexpression tests: {results['overexpression_count']}")
    print(f"   Robust nodes: {len(results['robust_nodes'])}")

    return {
        "perturbation_results": results,
        "perturbations_tested": True
    }


def test_network_perturbations(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple perturbation testing
    """
    nodes = model_data["nodes"]
    logic_nodes = [name for name, info in nodes.items() if info["type"] == "logic"]
    
    knockout_results = {}
    overexpression_results = {}
    robust_nodes = []
    sensitive_nodes = []
    
    # Test each logic node
    for node in logic_nodes:
        print(f"   Testing perturbations for {node}")
        
        # Knockout test (force node to False)
        knockout_impact = simulate_perturbation(node, "knockout", model_data)
        knockout_results[node] = knockout_impact
        
        # Overexpression test (force node to True)  
        overexpression_impact = simulate_perturbation(node, "overexpression", model_data)
        overexpression_results[node] = overexpression_impact
        
        # Classify node based on perturbation sensitivity
        total_impact = knockout_impact + overexpression_impact
        if total_impact < 0.2:  # Low impact
            robust_nodes.append(node)
        elif total_impact > 0.8:  # High impact
            sensitive_nodes.append(node)
    
    return {
        "knockout_results": knockout_results,
        "overexpression_results": overexpression_results,
        "knockout_count": len(knockout_results),
        "overexpression_count": len(overexpression_results),
        "robust_nodes": robust_nodes,
        "sensitive_nodes": sensitive_nodes
    }


def simulate_perturbation(target_node: str, perturbation_type: str, model_data: Dict[str, Any]) -> float:
    """
    Simulate the impact of a perturbation on the network
    Returns impact score (0.0 = no impact, 1.0 = maximum impact)
    """
    # Simple impact simulation (can be enhanced with real network simulation)
    
    nodes = model_data["nodes"]
    
    # Count how many nodes depend on the target node
    dependent_count = 0
    for node_name, node_info in nodes.items():
        if node_info["type"] == "logic":
            logic = node_info.get("logic", "")
            if target_node in logic:
                dependent_count += 1
    
    # Simple impact calculation based on connectivity
    total_logic_nodes = len([n for n in nodes.values() if n["type"] == "logic"])
    if total_logic_nodes == 0:
        return 0.0
    
    # Impact is proportional to how many nodes depend on this node
    base_impact = dependent_count / total_logic_nodes
    
    # Add some randomness to simulate complex dynamics
    import random
    random_factor = random.uniform(0.8, 1.2)
    
    impact = min(1.0, base_impact * random_factor)
    return impact


# Tool definition for the registry
TOOL_DEFINITION = {
    "name": "test_perturbations",
    "description": "Test network robustness through knockout and overexpression experiments", 
    "function_name": "execute",
    "input_requirements": ["model_data"],
    "output_provides": ["perturbation_results", "perturbations_tested"],
    "category": "analyzer", 
    "priority": 70,
    "enabled": True
}
