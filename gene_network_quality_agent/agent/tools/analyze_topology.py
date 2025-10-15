"""
Network Topology Analysis Tool
Analyzes the structural properties of gene networks
"""
import networkx as nx
from typing import Dict, Any, List


def execute_natural_language(context: str, model_path: str) -> str:
    """
    Analyze network topology and return natural language evaluation

    Args:
        context: Previous analysis context (natural language)
        model_path: Path to the .bnd file

    Returns:
        Natural language evaluation of the network topology
    """
    try:
        # We need to load the network first to analyze topology
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

        # Perform topology analysis
        topology_results = _analyze_topology_internal(model_data)

        # Generate natural language evaluation
        num_nodes = topology_results["num_nodes"]
        num_edges = topology_results["num_edges"]
        density = topology_results["density"]
        num_cycles = topology_results["num_cycles"]
        num_sccs = topology_results["num_sccs"]
        is_connected = topology_results["is_connected"]

        # Assess network characteristics
        connectivity_assessment = "well-connected" if density > 0.3 else "moderately connected" if density > 0.1 else "sparsely connected"
        cycle_assessment = "contains regulatory feedback loops" if num_cycles > 0 else "lacks feedback loops"
        structure_assessment = "highly modular" if num_sccs > num_nodes * 0.5 else "moderately modular" if num_sccs > 2 else "tightly integrated"

        evaluation = f"""**Topology Analysis Results**

**Network Structure:**
- **Nodes**: {num_nodes} regulatory elements
- **Edges**: {num_edges} regulatory interactions
- **Density**: {density:.3f} ({connectivity_assessment})
- **Connectivity**: {'Connected' if is_connected else 'Disconnected components detected'}

**Regulatory Architecture:**
- **Feedback Loops**: {num_cycles} cycles detected ({cycle_assessment})
- **Modularity**: {num_sccs} strongly connected components ({structure_assessment})

**Topological Assessment:**
The network shows {'robust' if density > 0.2 and num_cycles > 0 else 'moderate' if density > 0.1 else 'limited'} regulatory complexity. {'High connectivity and feedback loops suggest sophisticated regulatory control.' if density > 0.2 and num_cycles > 0 else 'Moderate connectivity indicates balanced regulatory interactions.' if density > 0.1 else 'Low connectivity may indicate missing regulatory relationships or a simplified model.'}

{'**Disconnected components detected** - some regulatory elements may be isolated.' if not is_connected else '**Well-connected network** - all elements participate in regulatory interactions.'}

**Implications for Dynamics**: {'Complex dynamics expected due to feedback loops and high connectivity.' if num_cycles > 0 and density > 0.2 else 'Moderate dynamics expected with some regulatory interactions.' if density > 0.1 else 'Simple dynamics likely due to limited connectivity.'}"""

        return evaluation

    except Exception as e:
        return f"**Topology Analysis Failed**: {str(e)}"


def _analyze_topology_internal(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """Internal topology analysis function"""
    # Create NetworkX graph
    G = nx.DiGraph()
    nodes = model_data["nodes"]

    # Add nodes
    for node_name, node_info in nodes.items():
        G.add_node(node_name, **node_info)

    # Add edges based on logic dependencies
    for node_name, node_info in nodes.items():
        if node_info["type"] == "logic":
            logic = node_info.get("logic", "")
            # Simple dependency extraction (can be enhanced)
            dependencies = extract_dependencies(logic, nodes.keys())
            for dep in dependencies:
                G.add_edge(dep, node_name)

    # Calculate topology metrics
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = nx.density(G) if num_nodes > 1 else 0

    # Find cycles
    try:
        cycles = list(nx.simple_cycles(G))
        num_cycles = len(cycles)
    except:
        cycles = []
        num_cycles = 0

    # Strongly connected components
    sccs = list(nx.strongly_connected_components(G))
    num_sccs = len(sccs)

    # Check connectivity
    is_connected = nx.is_weakly_connected(G) if num_nodes > 1 else True

    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "density": density,
        "num_cycles": num_cycles,
        "cycles": cycles,
        "num_sccs": num_sccs,
        "sccs": sccs,
        "is_connected": is_connected
    }


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze network topology and structure
    """
    model_data = state.get("model_data")
    if not model_data:
        raise ValueError("model_data not found in state")

    print("Analyzing topology...")

    # Use internal analysis function
    topology_results = _analyze_topology_internal(model_data)

    num_nodes = topology_results["num_nodes"]
    num_edges = topology_results["num_edges"]
    density = topology_results["density"]
    num_cycles = topology_results["num_cycles"]
    cycles = topology_results["cycles"]
    sccs = topology_results["sccs"]
    num_sccs = len(sccs)
    is_connected = topology_results["is_connected"]

    results = {
        "nodes": num_nodes,
        "edges": num_edges,
        "density": density,
        "cycles": num_cycles,
        "strongly_connected_components": num_sccs,
        "connected": is_connected,
        "cycle_details": cycles[:10]  # Store first 10 cycles
    }

    print(f"Topology analysis complete:")
    print(f"   Nodes: {num_nodes}")
    print(f"   Edges: {num_edges}")
    print(f"   Cycles: {num_cycles}")
    print(f"   Strongly connected components: {num_sccs}")
    
    return {
        "topology_results": results,
        "topology_analyzed": True
    }


def extract_dependencies(logic_str: str, available_nodes: List[str]) -> List[str]:
    """
    Extract node dependencies from logic string
    Simple implementation - can be enhanced with proper parsing
    """
    dependencies = []
    
    # Remove operators and parentheses, split by common separators
    cleaned = logic_str.replace("&", " ").replace("|", " ").replace("!", " ")
    cleaned = cleaned.replace("(", " ").replace(")", " ").replace("@logic", " ")
    cleaned = cleaned.replace("?", " ").replace(":", " ").replace("1", " ").replace("0", " ")
    
    tokens = cleaned.split()
    
    for token in tokens:
        token = token.strip()
        if token and token in available_nodes:
            dependencies.append(token)
    
    return list(set(dependencies))  # Remove duplicates


# Tool definition for the registry
TOOL_DEFINITION = {
    "name": "analyze_topology",
    "description": "Analyze network topology and structural properties",
    "function_name": "execute", 
    "input_requirements": ["model_data"],
    "output_provides": ["topology_results", "topology_analyzed"],
    "category": "analyzer",
    "priority": 90,
    "enabled": True
}
