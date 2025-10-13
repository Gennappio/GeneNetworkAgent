"""
Perturbation Analysis Node - Simulates knockout and overexpression effects
"""
from typing import Dict, Any, List
import copy


def perturb_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze network perturbations.
    Simple implementation for debugging.
    """
    print("🔄 Analyzing perturbations...")
    
    model = state.get("model")
    if not model:
        print("❌ No model to analyze")
        state["perturb"] = {"error": "No model available"}
        return state
    
    try:
        # Simple perturbation analysis
        perturbation_analysis = analyze_perturbations(model)
        
        print(f"✅ Perturbation analysis complete:")
        print(f"   Knockout tests: {len(perturbation_analysis['knockouts'])}")
        print(f"   Overexpression tests: {len(perturbation_analysis['overexpressions'])}")
        print(f"   Robust nodes: {len(perturbation_analysis['robust_nodes'])}")
        
        state["perturb"] = perturbation_analysis
        
    except Exception as e:
        print(f"❌ Error in perturbation analysis: {e}")
        state["perturb"] = {"error": str(e)}
    
    return state


def analyze_perturbations(model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple perturbation analysis.
    """
    nodes = model.get("nodes", {})
    input_conditions = model.get("input_conditions", {})
    
    # Get baseline behavior
    baseline_states = simulate_baseline(model)
    
    knockout_results = []
    overexpression_results = []
    robust_nodes = []
    sensitive_nodes = []
    
    # Test each non-input node
    logic_nodes = [name for name, data in nodes.items() if data.get("type") == "logic"]
    
    for node_name in logic_nodes:
        print(f"   Testing perturbations for {node_name}")
        
        # Test knockout (force to False)
        ko_result = test_knockout(model, node_name, baseline_states)
        knockout_results.append(ko_result)
        
        # Test overexpression (force to True)
        oe_result = test_overexpression(model, node_name, baseline_states)
        overexpression_results.append(oe_result)
        
        # Determine if node is robust or sensitive
        if ko_result["impact_score"] < 0.1 and oe_result["impact_score"] < 0.1:
            robust_nodes.append(node_name)
        elif ko_result["impact_score"] > 0.5 or oe_result["impact_score"] > 0.5:
            sensitive_nodes.append(node_name)
    
    return {
        "baseline_states": baseline_states,
        "knockouts": knockout_results,
        "overexpressions": overexpression_results,
        "robust_nodes": robust_nodes,
        "sensitive_nodes": sensitive_nodes,
        "total_nodes_tested": len(logic_nodes)
    }


def simulate_baseline(model: Dict[str, Any], steps: int = 50) -> Dict[str, bool]:
    """
    Simulate baseline network behavior.
    """
    nodes = model.get("nodes", {})
    input_conditions = model.get("input_conditions", {})
    
    # Use first input condition or default
    if input_conditions:
        condition_name = list(input_conditions.keys())[0]
        initial_state = input_conditions[condition_name].copy()
    else:
        initial_state = {}
    
    # Initialize all nodes
    current_state = {}
    for node_name, node_data in nodes.items():
        if node_data.get("type") == "input":
            current_state[node_name] = initial_state.get(node_name, False)
        else:
            current_state[node_name] = False  # Start with False for logic nodes
    
    # Simulate for several steps
    for step in range(steps):
        next_state = current_state.copy()
        
        # Update logic nodes
        for node_name, node_data in nodes.items():
            if node_data.get("type") == "logic":
                logic_rule = node_data.get("logic", "")
                next_state[node_name] = evaluate_logic_rule(logic_rule, current_state)
        
        # Check for steady state
        if next_state == current_state:
            break
        
        current_state = next_state
    
    return current_state


def test_knockout(model: Dict[str, Any], target_node: str, baseline_states: Dict[str, bool]) -> Dict[str, Any]:
    """
    Test knockout of a specific node.
    """
    # Create modified model
    modified_model = copy.deepcopy(model)
    
    # Force target node to False (knockout)
    if target_node in modified_model["nodes"]:
        modified_model["nodes"][target_node]["logic"] = "False"
    
    # Simulate with knockout
    ko_states = simulate_baseline(modified_model)
    
    # Calculate impact
    impact_score = calculate_impact(baseline_states, ko_states)
    affected_nodes = find_affected_nodes(baseline_states, ko_states)
    
    return {
        "node": target_node,
        "type": "knockout",
        "impact_score": impact_score,
        "affected_nodes": affected_nodes,
        "final_states": ko_states
    }


def test_overexpression(model: Dict[str, Any], target_node: str, baseline_states: Dict[str, bool]) -> Dict[str, Any]:
    """
    Test overexpression of a specific node.
    """
    # Create modified model
    modified_model = copy.deepcopy(model)
    
    # Force target node to True (overexpression)
    if target_node in modified_model["nodes"]:
        modified_model["nodes"][target_node]["logic"] = "True"
    
    # Simulate with overexpression
    oe_states = simulate_baseline(modified_model)
    
    # Calculate impact
    impact_score = calculate_impact(baseline_states, oe_states)
    affected_nodes = find_affected_nodes(baseline_states, oe_states)
    
    return {
        "node": target_node,
        "type": "overexpression",
        "impact_score": impact_score,
        "affected_nodes": affected_nodes,
        "final_states": oe_states
    }


def calculate_impact(baseline: Dict[str, bool], perturbed: Dict[str, bool]) -> float:
    """
    Calculate impact score as fraction of nodes that changed state.
    """
    if not baseline or not perturbed:
        return 0.0
    
    total_nodes = len(baseline)
    changed_nodes = 0
    
    for node_name in baseline:
        if node_name in perturbed and baseline[node_name] != perturbed[node_name]:
            changed_nodes += 1
    
    return changed_nodes / total_nodes if total_nodes > 0 else 0.0


def find_affected_nodes(baseline: Dict[str, bool], perturbed: Dict[str, bool]) -> List[str]:
    """
    Find nodes that changed state due to perturbation.
    """
    affected = []
    
    for node_name in baseline:
        if node_name in perturbed and baseline[node_name] != perturbed[node_name]:
            affected.append(node_name)
    
    return affected


def evaluate_logic_rule(logic_rule: str, state: Dict[str, bool]) -> bool:
    """
    Simple logic rule evaluation (same as in dynamics.py).
    """
    if not logic_rule:
        return False
    
    try:
        # Handle special cases
        if logic_rule.strip() == "True":
            return True
        if logic_rule.strip() == "False":
            return False
        
        # Replace gene names with their boolean values
        expr = logic_rule
        
        # Sort by length to avoid partial replacements
        gene_names = sorted(state.keys(), key=len, reverse=True)
        
        for gene_name in gene_names:
            if gene_name in expr:
                value = "True" if state[gene_name] else "False"
                expr = expr.replace(gene_name, value)
        
        # Replace logical operators
        expr = expr.replace('&', ' and ')
        expr = expr.replace('|', ' or ')
        expr = expr.replace('!', ' not ')
        
        return bool(eval(expr))
        
    except Exception as e:
        print(f"Warning: Error evaluating logic rule '{logic_rule}': {e}")
        return False
