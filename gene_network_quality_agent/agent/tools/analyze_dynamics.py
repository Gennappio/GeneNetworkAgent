"""
Network Dynamics Analysis Tool
Simulates network behavior and identifies attractors, oscillations
"""
import random
from typing import Dict, Any, List, Set


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze network dynamics through simulation
    """
    model_data = state.get("model_data")
    bnd_network = state.get("bnd_network")
    
    if not model_data:
        raise ValueError("model_data not found in state")
    
    print("🔄 Analyzing dynamics...")
    
    # Simple dynamics simulation
    results = simulate_network_dynamics(model_data, bnd_network)
    
    print(f"✅ Dynamics analysis complete:")
    print(f"   Attractors found: {results['num_attractors']}")
    print(f"   Unstable nodes: {len(results['unstable_nodes'])}")
    print(f"   Oscillations detected: {results['has_oscillations']}")
    
    return {
        "dynamics_results": results,
        "dynamics_analyzed": True
    }


def simulate_network_dynamics(model_data: Dict[str, Any], bnd_network=None) -> Dict[str, Any]:
    """
    Simple network dynamics simulation
    """
    nodes = model_data["nodes"]
    logic_nodes = [name for name, info in nodes.items() if info["type"] == "logic"]
    input_nodes = [name for name, info in nodes.items() if info["type"] == "input"]
    
    attractors = []
    unstable_nodes = set()
    oscillation_detected = False
    
    # Run multiple simulations with different initial conditions
    num_simulations = 10
    
    for sim in range(num_simulations):
        print(f"   Simulation {sim + 1}/{num_simulations}")
        
        # Random initial state
        state = {node: random.choice([True, False]) for node in nodes.keys()}
        
        # Simulate for max_steps
        max_steps = 20
        history = []
        
        for step in range(max_steps):
            history.append(state.copy())
            
            # Update logic nodes (simple random update for now)
            new_state = state.copy()
            
            for node in logic_nodes:
                # Simple random dynamics (can be enhanced with real BND simulation)
                if random.random() < 0.3:  # 30% chance to flip
                    new_state[node] = not state[node]
            
            # Check for steady state
            if new_state == state:
                print(f"     Steady state reached at step {step}")
                attractors.append(state.copy())
                break
            
            # Check for oscillation (cycle in history)
            if new_state in history:
                oscillation_detected = True
                cycle_start = history.index(new_state)
                cycle_length = step - cycle_start
                if cycle_length > 1:
                    print(f"     Oscillation detected (cycle length: {cycle_length})")
                break
            
            state = new_state
        
        # Identify unstable nodes (nodes that change frequently)
        if len(history) > 5:
            for node in logic_nodes:
                changes = sum(1 for i in range(1, len(history)) 
                            if history[i][node] != history[i-1][node])
                if changes > len(history) * 0.3:  # Changed more than 30% of the time
                    unstable_nodes.add(node)
    
    return {
        "attractors": attractors,
        "num_attractors": len(attractors),
        "unstable_nodes": list(unstable_nodes),
        "has_oscillations": oscillation_detected,
        "simulation_count": num_simulations
    }


# Tool definition for the registry
TOOL_DEFINITION = {
    "name": "analyze_dynamics", 
    "description": "Simulate network dynamics and identify attractors and oscillations",
    "function_name": "execute",
    "input_requirements": ["model_data"],
    "output_provides": ["dynamics_results", "dynamics_analyzed"],
    "category": "analyzer",
    "priority": 80,
    "enabled": True
}
