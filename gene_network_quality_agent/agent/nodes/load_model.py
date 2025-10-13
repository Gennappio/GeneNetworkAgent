"""
Load Model Node - Loads gene network from BND files using gene_network_standalone.py
"""
import yaml
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path to import gene_network_standalone
parent_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from gene_network_standalone import StandaloneGeneNetwork
except ImportError as e:
    print(f"Warning: Could not import gene_network_standalone: {e}")
    StandaloneGeneNetwork = None


def load_model_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load gene network model from BND files using gene_network_standalone.py
    """
    print("🔄 Loading model...")

    model_path = state.get("model_path", "models/example_network.bnd")

    try:
        # Check if file exists
        if not os.path.exists(model_path):
            print(f"❌ Model file not found: {model_path}")
            state["model"] = None
            state["error"] = f"Model file not found: {model_path}"
            return state

        # Load BND model using gene_network_standalone.py
        if model_path.endswith('.bnd'):
            if StandaloneGeneNetwork is None:
                print(f"❌ Cannot load BND file: gene_network_standalone not available")
                state["model"] = None
                state["error"] = "gene_network_standalone not available"
                return state

            print(f"📝 Loading BND file: {model_path}")

            # Load using StandaloneGeneNetwork
            network = StandaloneGeneNetwork()
            nodes_created = network.load_bnd_file(model_path)

            # Convert to standard format
            model_data = convert_bnd_to_standard_format(network, model_path)

            print(f"✅ Loaded BND model: {model_data.get('name', 'Unknown')}")
            print(f"   Total nodes: {len(model_data.get('nodes', {}))}")
            print(f"   Input nodes: {len([n for n in model_data.get('nodes', {}).values() if n.get('type') == 'input'])}")
            print(f"   Logic nodes: {len([n for n in model_data.get('nodes', {}).values() if n.get('type') == 'logic'])}")

            state["model"] = model_data
            state["model_type"] = "bnd"
            state["bnd_network"] = network  # Store original network for dynamics simulation

        # Legacy YAML support (for backward compatibility)
        elif model_path.endswith('.yaml') or model_path.endswith('.yml'):
            with open(model_path, 'r') as f:
                model_data = yaml.safe_load(f)

            print(f"✅ Loaded YAML model: {model_data.get('name', 'Unknown')}")
            print(f"   Nodes: {len(model_data.get('nodes', {}))}")

            state["model"] = model_data
            state["model_type"] = "yaml"

        else:
            print(f"❌ Unsupported file format: {model_path}")
            print("   Supported formats: .bnd")
            state["model"] = None
            state["error"] = f"Unsupported file format: {model_path}"

    except Exception as e:
        print(f"❌ Error loading model: {e}")
        state["model"] = None
        state["error"] = str(e)

    return state


def convert_bnd_to_standard_format(network: Any, model_path: str) -> Dict[str, Any]:
    """
    Convert BND network to standard format for analysis.
    """
    # Extract filename for network name
    filename = os.path.basename(model_path)
    network_name = filename.replace('.bnd', '').replace('_', ' ').title()

    # Convert nodes
    nodes = {}
    for node_name, node in network.nodes.items():
        node_type = "input" if node.is_input else "logic"

        nodes[node_name] = {
            "type": node_type,
            "logic": node.logic_rule if hasattr(node, 'logic_rule') else "",
            "description": f"{'Input' if node.is_input else 'Logic'} node from BND file"
        }

    return {
        "name": network_name,
        "description": f"Gene network loaded from {model_path}",
        "nodes": nodes,
        "bnd_file": model_path,
        "total_nodes": len(nodes),
        "input_nodes": len(network.input_nodes),
        "logic_nodes": len(nodes) - len(network.input_nodes)
    }


def validate_model_structure(model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple validation of model structure.
    """
    issues = []
    
    if not model:
        return {"valid": False, "issues": ["Model is None or empty"]}
    
    # Check required fields
    if "nodes" not in model:
        issues.append("Missing 'nodes' section")
        
    nodes = model.get("nodes", {})
    if not nodes:
        issues.append("No nodes defined")
        
    # Check node structure
    input_nodes = []
    logic_nodes = []
    
    for node_name, node_data in nodes.items():
        node_type = node_data.get("type", "unknown")
        
        if node_type == "input":
            input_nodes.append(node_name)
        elif node_type == "logic":
            logic_nodes.append(node_name)
            if "logic" not in node_data:
                issues.append(f"Logic node '{node_name}' missing logic rule")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "input_nodes": input_nodes,
        "logic_nodes": logic_nodes,
        "total_nodes": len(nodes)
    }
