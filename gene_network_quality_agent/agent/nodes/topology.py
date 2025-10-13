"""
Topology Analysis Node - Analyzes network structure, circuits, and signals
"""
import networkx as nx
from typing import Dict, Any, List, Set
import re


def topology_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze network topology.
    Simple implementation for debugging.
    """
    print("🔄 Analyzing topology...")
    
    model = state.get("model")
    if not model:
        print("❌ No model to analyze")
        state["topology"] = {"error": "No model available"}
        return state
    
    try:
        # Create NetworkX graph
        G = nx.DiGraph()
        nodes = model.get("nodes", {})
        
        # Add nodes
        for node_name, node_data in nodes.items():
            node_type = node_data.get("type", "unknown")
            G.add_node(node_name, type=node_type)
        
        # Add edges based on logic rules
        for node_name, node_data in nodes.items():
            if node_data.get("type") == "logic":
                logic_rule = node_data.get("logic", "")
                dependencies = extract_dependencies(logic_rule)
                
                for dep in dependencies:
                    if dep in nodes:
                        G.add_edge(dep, node_name)
        
        # Analyze topology
        analysis = analyze_network_structure(G, nodes)
        
        print(f"✅ Topology analysis complete:")
        print(f"   Nodes: {analysis['node_count']}")
        print(f"   Edges: {analysis['edge_count']}")
        print(f"   Cycles: {len(analysis['cycles'])}")
        print(f"   Strongly connected components: {analysis['scc_count']}")
        
        state["topology"] = analysis
        
    except Exception as e:
        print(f"❌ Error in topology analysis: {e}")
        state["topology"] = {"error": str(e)}
    
    return state


def extract_dependencies(logic_rule: str) -> Set[str]:
    """
    Extract gene dependencies from logic rule.
    Simple regex-based extraction.
    """
    if not logic_rule:
        return set()
    
    # Find all gene names (alphanumeric + underscore)
    gene_names = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', logic_rule)
    
    # Filter out boolean operators
    keywords = {'and', 'or', 'not', 'True', 'False', 'true', 'false', '&', '|', '!'}
    dependencies = {name for name in gene_names if name not in keywords}
    
    return dependencies


def analyze_network_structure(G: nx.DiGraph, nodes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze network structure using NetworkX.
    """
    analysis = {
        "node_count": G.number_of_nodes(),
        "edge_count": G.number_of_edges(),
        "density": nx.density(G),
        "is_connected": nx.is_weakly_connected(G),
        "cycles": [],
        "scc_count": 0,
        "input_nodes": [],
        "output_nodes": [],
        "logic_nodes": [],
        "node_degrees": {}
    }
    
    # Find cycles
    try:
        cycles = list(nx.simple_cycles(G))
        analysis["cycles"] = cycles[:10]  # Limit to first 10 cycles
    except:
        analysis["cycles"] = []
    
    # Strongly connected components
    try:
        sccs = list(nx.strongly_connected_components(G))
        analysis["scc_count"] = len(sccs)
        analysis["largest_scc_size"] = max(len(scc) for scc in sccs) if sccs else 0
    except:
        analysis["scc_count"] = 0
        analysis["largest_scc_size"] = 0
    
    # Categorize nodes
    for node_name, node_data in nodes.items():
        node_type = node_data.get("type", "unknown")
        
        if node_type == "input":
            analysis["input_nodes"].append(node_name)
        elif node_type == "logic":
            analysis["logic_nodes"].append(node_name)
        
        # Check if it's an output node (no outgoing edges)
        if G.out_degree(node_name) == 0:
            analysis["output_nodes"].append(node_name)
        
        # Store degree information
        analysis["node_degrees"][node_name] = {
            "in_degree": G.in_degree(node_name),
            "out_degree": G.out_degree(node_name)
        }
    
    return analysis


def find_feedback_loops(G: nx.DiGraph) -> List[List[str]]:
    """
    Find feedback loops in the network.
    """
    try:
        cycles = list(nx.simple_cycles(G))
        return cycles
    except:
        return []


def identify_critical_nodes(G: nx.DiGraph) -> Dict[str, float]:
    """
    Identify critical nodes using centrality measures.
    """
    try:
        centrality = {}
        
        # Betweenness centrality
        betweenness = nx.betweenness_centrality(G)
        
        # In-degree centrality
        in_degree = nx.in_degree_centrality(G)
        
        # Out-degree centrality  
        out_degree = nx.out_degree_centrality(G)
        
        for node in G.nodes():
            centrality[node] = {
                "betweenness": betweenness.get(node, 0),
                "in_degree": in_degree.get(node, 0),
                "out_degree": out_degree.get(node, 0)
            }
        
        return centrality
        
    except Exception as e:
        print(f"Warning: Could not calculate centrality: {e}")
        return {}
