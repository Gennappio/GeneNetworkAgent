"""
Deep Topology Analysis Tool
Enhanced topology analysis with advanced graph metrics
This demonstrates how to add new tools to the system
"""
import networkx as nx
from typing import Dict, Any, List


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform deep topology analysis with advanced metrics
    """
    topology_results = state.get("topology_results")
    model_data = state.get("model_data")
    
    if not topology_results or not model_data:
        raise ValueError("topology_results and model_data required for deep analysis")
    
    print("🔄 Performing deep topology analysis...")
    
    # Get the graph from previous topology analysis
    G = topology_results.get("graph")
    if not G:
        print("⚠️  No graph found in topology_results, creating new one...")
        G = create_graph_from_model(model_data)
    
    # Advanced topology metrics
    results = calculate_advanced_metrics(G)
    
    print(f"✅ Deep topology analysis complete:")
    print(f"   Centrality analysis: {len(results['centrality_scores'])} nodes")
    print(f"   Community detection: {results['num_communities']} communities")
    print(f"   Network efficiency: {results['efficiency']:.3f}")
    
    return {
        "deep_topology_results": results,
        "topology_deep_analyzed": True
    }


def create_graph_from_model(model_data: Dict[str, Any]) -> nx.DiGraph:
    """Create NetworkX graph from model data"""
    G = nx.DiGraph()
    nodes = model_data["nodes"]
    
    # Add nodes
    for node_name, node_info in nodes.items():
        G.add_node(node_name, **node_info)
    
    # Add edges based on logic dependencies
    for node_name, node_info in nodes.items():
        if node_info["type"] == "logic":
            logic = node_info.get("logic", "")
            dependencies = extract_dependencies(logic, nodes.keys())
            for dep in dependencies:
                G.add_edge(dep, node_name)
    
    return G


def extract_dependencies(logic_str: str, available_nodes: List[str]) -> List[str]:
    """Extract node dependencies from logic string"""
    dependencies = []
    cleaned = logic_str.replace("&", " ").replace("|", " ").replace("!", " ")
    cleaned = cleaned.replace("(", " ").replace(")", " ").replace("@logic", " ")
    cleaned = cleaned.replace("?", " ").replace(":", " ").replace("1", " ").replace("0", " ")
    
    tokens = cleaned.split()
    for token in tokens:
        token = token.strip()
        if token and token in available_nodes:
            dependencies.append(token)
    
    return list(set(dependencies))


def calculate_advanced_metrics(G: nx.DiGraph) -> Dict[str, Any]:
    """Calculate advanced graph topology metrics"""
    
    results = {
        "centrality_scores": {},
        "clustering_coefficient": 0.0,
        "efficiency": 0.0,
        "num_communities": 0,
        "communities": [],
        "motif_counts": {},
        "path_analysis": {}
    }
    
    if G.number_of_nodes() == 0:
        return results
    
    # Centrality measures
    try:
        results["centrality_scores"] = {
            "betweenness": dict(nx.betweenness_centrality(G)),
            "closeness": dict(nx.closeness_centrality(G)),
            "degree": dict(nx.degree_centrality(G)),
            "eigenvector": dict(nx.eigenvector_centrality(G, max_iter=100))
        }
    except:
        # Fallback for problematic graphs
        results["centrality_scores"] = {
            "degree": dict(nx.degree_centrality(G))
        }
    
    # Clustering coefficient
    try:
        # Convert to undirected for clustering
        G_undirected = G.to_undirected()
        results["clustering_coefficient"] = nx.average_clustering(G_undirected)
    except:
        results["clustering_coefficient"] = 0.0
    
    # Network efficiency
    try:
        if nx.is_connected(G.to_undirected()):
            results["efficiency"] = nx.global_efficiency(G)
        else:
            results["efficiency"] = nx.local_efficiency(G)
    except:
        results["efficiency"] = 0.0
    
    # Community detection (simple approach)
    try:
        G_undirected = G.to_undirected()
        if G_undirected.number_of_edges() > 0:
            # Use simple connected components as communities
            communities = list(nx.connected_components(G_undirected))
            results["num_communities"] = len(communities)
            results["communities"] = [list(community) for community in communities]
        else:
            results["num_communities"] = G.number_of_nodes()
            results["communities"] = [[node] for node in G.nodes()]
    except:
        results["num_communities"] = 1
        results["communities"] = [list(G.nodes())]
    
    # Simple motif counting (3-node patterns)
    try:
        motif_counts = count_simple_motifs(G)
        results["motif_counts"] = motif_counts
    except:
        results["motif_counts"] = {}
    
    # Path analysis
    try:
        if G.number_of_nodes() > 1:
            # Average shortest path length
            if nx.is_weakly_connected(G):
                avg_path_length = nx.average_shortest_path_length(G)
                results["path_analysis"]["average_path_length"] = avg_path_length
            
            # Diameter
            if nx.is_strongly_connected(G):
                diameter = nx.diameter(G)
                results["path_analysis"]["diameter"] = diameter
    except:
        results["path_analysis"] = {"average_path_length": 0, "diameter": 0}
    
    return results


def count_simple_motifs(G: nx.DiGraph) -> Dict[str, int]:
    """Count simple 3-node motifs in the graph"""
    motifs = {
        "feed_forward_loop": 0,
        "feedback_loop": 0,
        "cascade": 0
    }
    
    nodes = list(G.nodes())
    
    # Check all 3-node combinations
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            for k in range(j+1, len(nodes)):
                a, b, c = nodes[i], nodes[j], nodes[k]
                
                # Get edges between these nodes
                edges = []
                if G.has_edge(a, b): edges.append((a, b))
                if G.has_edge(b, a): edges.append((b, a))
                if G.has_edge(a, c): edges.append((a, c))
                if G.has_edge(c, a): edges.append((c, a))
                if G.has_edge(b, c): edges.append((b, c))
                if G.has_edge(c, b): edges.append((c, b))
                
                # Classify motif type
                if len(edges) >= 3:
                    # Check for feed-forward loop: A->B, A->C, B->C
                    if (a, b) in edges and (a, c) in edges and (b, c) in edges:
                        motifs["feed_forward_loop"] += 1
                    
                    # Check for feedback loop: A->B, B->C, C->A
                    elif (a, b) in edges and (b, c) in edges and (c, a) in edges:
                        motifs["feedback_loop"] += 1
                    
                    # Check for cascade: A->B->C (linear)
                    elif len(edges) == 2 and ((a, b) in edges and (b, c) in edges):
                        motifs["cascade"] += 1
    
    return motifs


# Tool definition for the registry
TOOL_DEFINITION = {
    "name": "deep_topology_analysis",
    "description": "Advanced topology analysis with centrality, communities, and motifs",
    "function_name": "execute",
    "input_requirements": ["topology_results", "model_data"],
    "output_provides": ["deep_topology_results", "topology_deep_analyzed"],
    "category": "analyzer",
    "priority": 85,  # High priority for deep analysis
    "enabled": True
}
