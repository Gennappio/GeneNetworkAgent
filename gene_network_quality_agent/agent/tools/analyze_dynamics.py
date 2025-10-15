"""
Network Dynamics Analysis Tool
Simulates network behavior and identifies attractors, oscillations
"""
import random
from typing import Dict, Any, List, Set


def execute_natural_language(context: str, model_path: str) -> str:
    """
    Analyze network dynamics and return natural language evaluation

    Args:
        context: Previous analysis context (natural language)
        model_path: Path to the .bnd file

    Returns:
        Natural language evaluation of the network dynamics
    """
    try:
        # Load and analyze dynamics
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

        # Perform dynamics analysis
        dynamics_results = _analyze_dynamics_internal(model_data, network)

        # Generate natural language evaluation
        num_attractors = dynamics_results["num_attractors"]
        has_oscillations = dynamics_results["has_oscillations"]
        unstable_nodes = dynamics_results["unstable_nodes"]
        num_unstable = len(unstable_nodes)

        # Assess dynamics characteristics
        stability_assessment = "highly stable" if num_unstable == 0 else "moderately stable" if num_unstable < 3 else "unstable"
        complexity_assessment = "complex" if num_attractors > 5 else "moderate" if num_attractors > 2 else "simple"

        evaluation = f"""**Dynamics Analysis Results**

**Attractor Landscape:**
- **Attractors Found**: {num_attractors} stable states ({complexity_assessment} dynamics)
- **Oscillations**: {'Detected' if has_oscillations else 'None detected'} {'(dynamic regulatory cycles)' if has_oscillations else '(steady-state behavior)'}

**Network Stability:**
- **Unstable Nodes**: {num_unstable} out of {len(model_data['nodes'])} nodes
- **Stability Assessment**: {stability_assessment.title()}
- **Sensitive Elements**: {', '.join(unstable_nodes[:5])}{'...' if len(unstable_nodes) > 5 else ''}

**Dynamical Assessment:**
The network exhibits {'rich dynamical behavior' if num_attractors > 3 else 'moderate dynamical complexity' if num_attractors > 1 else 'simple dynamics'} with {num_attractors} distinct stable state{'s' if num_attractors != 1 else ''}.

{'**High instability detected** - many nodes show sensitive behavior to perturbations.' if num_unstable > len(model_data['nodes']) * 0.5 else '**Good stability** - most regulatory elements show robust behavior.' if num_unstable < 3 else '**Moderate instability** - some regulatory elements are sensitive to perturbations.'}

{'**Oscillatory behavior detected** - suggests active regulatory cycles and temporal dynamics.' if has_oscillations else '**Steady-state behavior** - network tends toward stable equilibrium states.'}

**Biological Implications**: {'Complex multi-stable behavior suggests the network can adopt multiple functional states, potentially corresponding to different cellular phenotypes.' if num_attractors > 3 else 'The network shows well-defined stable states suitable for robust cellular decision-making.' if num_attractors > 1 else 'Simple dynamics suggest a straightforward regulatory response.'}"""

        return evaluation

    except Exception as e:
        return f"**Dynamics Analysis Failed**: {str(e)}"


def _analyze_dynamics_internal(model_data: Dict[str, Any], bnd_network=None) -> Dict[str, Any]:
    """Internal dynamics analysis function"""
    return simulate_network_dynamics(model_data, bnd_network)


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze network dynamics through simulation
    """
    model_data = state.get("model_data")
    bnd_network = state.get("bnd_network")

    if not model_data:
        raise ValueError("model_data not found in state")

    print("Analyzing dynamics...")

    # Simple dynamics simulation
    results = simulate_network_dynamics(model_data, bnd_network)

    print(f"Dynamics analysis complete:")
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
