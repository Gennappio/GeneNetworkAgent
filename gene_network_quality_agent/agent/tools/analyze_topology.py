"""
Network Topology Analysis Tool
Analyzes the structural properties of gene networks
"""
import networkx as nx
from typing import Dict, Any, List


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze network topology and structure
    """
    model_data = state.get("model_data")
    if not model_data:
        raise ValueError("model_data not found in state")
    
    print("🔄 Analyzing topology...")
    
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
    is_connected = nx.is_weakly_connected(G)
    
    results = {
        "nodes": num_nodes,
        "edges": num_edges,
        "density": density,
        "cycles": num_cycles,
        "strongly_connected_components": num_sccs,
        "connected": is_connected,
        "cycle_details": cycles[:10]  # Store first 10 cycles
    }
    
    print(f"✅ Topology analysis complete:")
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
