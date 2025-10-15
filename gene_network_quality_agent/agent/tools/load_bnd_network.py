"""
BND Network Loader Tool
Loads and parses .bnd files using gene_network_standalone.py
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path to import gene_network_standalone
parent_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from gene_network_standalone import StandaloneGeneNetwork
except ImportError:
    print("⚠️  Could not import StandaloneGeneNetwork")
    StandaloneGeneNetwork = None


def execute_natural_language(context: str, model_path: str) -> str:
    """
    Load BND network file and return natural language evaluation

    Args:
        context: Previous analysis context (natural language)
        model_path: Path to the .bnd file

    Returns:
        Natural language evaluation of the network loading process
    """
    try:
        if not StandaloneGeneNetwork:
            return "**Network Loading Failed**: StandaloneGeneNetwork not available. Cannot load BND files."

        # Load the BND file
        network = StandaloneGeneNetwork()
        nodes_created = network.load_bnd_file(model_path)

        # Convert to standard format for analysis
        model_data = convert_bnd_to_standard_format(network, model_path)

        # Determine network name
        network_name = Path(model_path).stem.replace("_", " ").title()

        # Count different node types
        input_nodes = len([n for n in model_data['nodes'].values() if n['type'] == 'input'])
        logic_nodes = len([n for n in model_data['nodes'].values() if n['type'] == 'logic'])
        total_nodes = len(model_data['nodes'])

        # Generate natural language evaluation
        evaluation = f"""**Network Successfully Loaded**: {network_name}

**Network Composition:**
- **Total Nodes**: {total_nodes}
- **Input Nodes**: {input_nodes} (external signals/conditions)
- **Logic Nodes**: {logic_nodes} (internal regulatory elements)

**Loading Assessment:**
The network file was successfully parsed and loaded. The network contains {total_nodes} regulatory elements, which suggests {'a complex' if total_nodes > 10 else 'a moderate' if total_nodes > 5 else 'a simple'} regulatory system.

The presence of {input_nodes} input nodes indicates the network can respond to {input_nodes} external signal{'s' if input_nodes != 1 else ''}, while {logic_nodes} internal nodes suggest {'complex' if logic_nodes > 8 else 'moderate' if logic_nodes > 4 else 'simple'} internal regulatory logic.

**Network Readiness**: Ready for topology, dynamics, and biological analysis."""

        return evaluation

    except Exception as e:
        return f"**Network Loading Failed**: {str(e)}"


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load BND network file and convert to standard format
    """
    model_path = state.get("model_path")
    if not model_path:
        raise ValueError("model_path not provided in state")
    
    print(f"Loading BND file: {model_path}")

    if not StandaloneGeneNetwork:
        raise ImportError("StandaloneGeneNetwork not available")

    # Load the BND file
    network = StandaloneGeneNetwork()
    nodes_created = network.load_bnd_file(model_path)

    print(f"Loading gene network from {model_path}")
    print(f"Created {nodes_created} nodes ({len(network.input_nodes)} input nodes)")

    # Convert to standard format
    model_data = convert_bnd_to_standard_format(network, model_path)

    # Determine network name from file
    network_name = Path(model_path).stem.replace("_", " ").title()

    print(f"Loaded BND model: {network_name}")
    print(f"   Total nodes: {len(model_data['nodes'])}")
    print(f"   Input nodes: {len([n for n in model_data['nodes'].values() if n['type'] == 'input'])}")
    print(f"   Logic nodes: {len([n for n in model_data['nodes'].values() if n['type'] == 'logic'])}")
    
    return {
        "model_data": model_data,
        "bnd_network": network,  # Store for dynamics simulation
        "network_name": network_name,
        "network_loaded": True
    }


def convert_bnd_to_standard_format(network: Any, model_path: str) -> Dict[str, Any]:
    """Convert BND network to standard analysis format"""
    
    nodes = {}
    
    # Add input nodes
    for input_node in network.input_nodes:
        nodes[input_node] = {
            "type": "input",
            "description": f"Input node {input_node}"
        }
    
    # Add logic nodes
    for node_name, node_obj in network.nodes.items():
        if node_name not in network.input_nodes:
            # Extract logic from the node object
            logic_str = "unknown"
            if hasattr(node_obj, 'logic') and node_obj.logic:
                logic_str = str(node_obj.logic)
            
            nodes[node_name] = {
                "type": "logic",
                "logic": logic_str,
                "description": f"Logic node {node_name}"
            }
    
    return {
        "name": Path(model_path).stem.replace("_", " ").title(),
        "description": f"Gene network loaded from {model_path}",
        "nodes": nodes
    }


# Tool definition for the registry
TOOL_DEFINITION = {
    "name": "load_bnd_network",
    "description": "Load and parse BND gene network files",
    "function_name": "execute",
    "input_requirements": ["model_path"],
    "output_provides": ["model_data", "bnd_network", "network_name", "network_loaded"],
    "category": "loader",
    "priority": 100,  # High priority - usually needed first
    "enabled": True
}
