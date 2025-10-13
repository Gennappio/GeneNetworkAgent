"""
Dynamics Analysis Node - Simulates network dynamics and identifies attractors
"""
from typing import Dict, Any, List, Tuple, Set
import random


def dynamics_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze network dynamics.
    Simple implementation for debugging.
    """
    print("🔄 Analyzing dynamics...")
    
    model = state.get("model")
    if not model:
        print("❌ No model to analyze")
        state["dynamics"] = {"error": "No model available"}
        return state
    
    try:
        # Simple dynamics simulation
        dynamics_analysis = simulate_dynamics(model)
        
        print(f"✅ Dynamics analysis complete:")
        print(f"   Attractors found: {len(dynamics_analysis['attractors'])}")
        print(f"   Unstable nodes: {len(dynamics_analysis['unstable_nodes'])}")
        print(f"   Oscillations detected: {dynamics_analysis['has_oscillations']}")
        
        state["dynamics"] = dynamics_analysis
        
    except Exception as e:
        print(f"❌ Error in dynamics analysis: {e}")
        state["dynamics"] = {"error": str(e)}
    
    return state


def simulate_dynamics(model: Dict[str, Any], num_simulations: int = 10, max_steps: int = 100) -> Dict[str, Any]:
    """
    Simple dynamics simulation.
    """
    nodes = model.get("nodes", {})
    input_conditions = model.get("input_conditions", {})
    
    attractors = []
    unstable_nodes = set()
    oscillation_detected = False
    
    # Run multiple simulations with different initial conditions
    for sim in range(num_simulations):
        print(f"   Simulation {sim + 1}/{num_simulations}")
        
        # Use first input condition or random initialization
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
                current_state[node_name] = random.choice([True, False])
        
        # Simulate dynamics
        trajectory = simulate_single_trajectory(nodes, current_state, max_steps)
        
        # Analyze trajectory
        attractor = find_attractor(trajectory)
        if attractor:
            attractors.append(attractor)
        
        # Check for oscillations
        if detect_oscillation(trajectory):
            oscillation_detected = True
        
        # Identify unstable nodes
        unstable = find_unstable_nodes(trajectory)
        unstable_nodes.update(unstable)
    
    return {
        "attractors": attractors,
        "unstable_nodes": list(unstable_nodes),
        "has_oscillations": oscillation_detected,
        "num_simulations": num_simulations,
        "max_steps": max_steps
    }


def simulate_single_trajectory(nodes: Dict[str, Any], initial_state: Dict[str, bool], max_steps: int) -> List[Dict[str, bool]]:
    """
    Simulate a single trajectory.
    """
    trajectory = [initial_state.copy()]
    current_state = initial_state.copy()
    
    for step in range(max_steps):
        next_state = current_state.copy()
        
        # Update logic nodes
        for node_name, node_data in nodes.items():
            if node_data.get("type") == "logic":
                logic_rule = node_data.get("logic", "")
                next_state[node_name] = evaluate_logic_rule(logic_rule, current_state)
        
        trajectory.append(next_state.copy())
        
        # Check for steady state
        if next_state == current_state:
            print(f"     Steady state reached at step {step + 1}")
            break
        
        current_state = next_state
    
    return trajectory


def evaluate_logic_rule(logic_rule: str, state: Dict[str, bool]) -> bool:
    """
    Simple logic rule evaluation.
    """
    if not logic_rule:
        return False
    
    try:
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


def find_attractor(trajectory: List[Dict[str, bool]]) -> Dict[str, Any]:
    """
    Find attractor in trajectory.
    """
    if len(trajectory) < 2:
        return None
    
    # Check for fixed point (last state)
    last_state = trajectory[-1]
    if len(trajectory) >= 2 and trajectory[-1] == trajectory[-2]:
        return {
            "type": "fixed_point",
            "state": last_state,
            "period": 1
        }
    
    # Check for limit cycle (simple check)
    for period in range(2, min(10, len(trajectory) // 2)):
        if len(trajectory) >= 2 * period:
            cycle_states = trajectory[-period:]
            prev_cycle = trajectory[-2*period:-period]
            
            if cycle_states == prev_cycle:
                return {
                    "type": "limit_cycle",
                    "states": cycle_states,
                    "period": period
                }
    
    return None


def detect_oscillation(trajectory: List[Dict[str, bool]]) -> bool:
    """
    Simple oscillation detection.
    """
    if len(trajectory) < 4:
        return False
    
    # Check if any node oscillates in the last few steps
    for node_name in trajectory[0].keys():
        last_values = [state[node_name] for state in trajectory[-4:]]
        if len(set(last_values)) > 1:  # Values change
            return True
    
    return False


def find_unstable_nodes(trajectory: List[Dict[str, bool]]) -> Set[str]:
    """
    Find nodes that change frequently.
    """
    if len(trajectory) < 5:
        return set()
    
    unstable = set()
    
    for node_name in trajectory[0].keys():
        # Count state changes in trajectory
        changes = 0
        for i in range(1, len(trajectory)):
            if trajectory[i][node_name] != trajectory[i-1][node_name]:
                changes += 1
        
        # If node changes more than 20% of the time, consider it unstable
        if changes > len(trajectory) * 0.2:
            unstable.add(node_name)
    
    return unstable
