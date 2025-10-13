#!/usr/bin/env python3
"""
Integration test showing how to integrate with gene_network_standalone.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import gene_network_standalone
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from gene_network_standalone import StandaloneGeneNetwork
    print("✅ Successfully imported gene_network_standalone")
except ImportError as e:
    print(f"❌ Could not import gene_network_standalone: {e}")
    sys.exit(1)

def test_bnd_integration():
    """
    Test integration with existing BND file functionality.
    """
    print("🧪 Testing BND integration...")
    
    # Check if BND file exists
    bnd_file = parent_dir / "jaya_microc.bnd"
    if not bnd_file.exists():
        print(f"❌ BND file not found: {bnd_file}")
        return False
    
    try:
        # Load BND file using existing code
        network = StandaloneGeneNetwork()
        nodes_created = network.load_bnd_file(str(bnd_file))
        
        print(f"✅ Loaded BND file successfully")
        print(f"   Nodes created: {nodes_created}")
        print(f"   Input nodes: {len(network.input_nodes)}")
        print(f"   Total nodes: {len(network.nodes)}")
        
        # Show some example nodes
        print(f"\n📋 Example nodes:")
        for i, (name, node) in enumerate(network.nodes.items()):
            if i >= 5:  # Show first 5 nodes
                break
            node_type = "INPUT" if node.is_input else "LOGIC"
            logic = node.logic_rule if hasattr(node, 'logic_rule') else "N/A"
            print(f"   {name} ({node_type}): {logic}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading BND file: {e}")
        return False

def show_integration_plan():
    """
    Show how full integration would work.
    """
    print("\n🔧 INTEGRATION PLAN")
    print("="*50)
    print("""
To fully integrate with gene_network_standalone.py:

1. Modify load_model.py:
   - Import StandaloneGeneNetwork
   - Use network.load_bnd_file() for .bnd files
   - Convert network structure to standard format

2. Enhance dynamics.py:
   - Use network.simulate() for realistic dynamics
   - Leverage existing NetLogo-style updates
   - Use network.reset() and network.set_input_states()

3. Improve perturb.py:
   - Use network perturbation capabilities
   - Test with actual input conditions
   - Analyze real knockout/overexpression effects

4. Add LLM integration to validate.py:
   - Connect to OpenAI/Anthropic APIs
   - Use biological knowledge for validation
   - Generate pathway-specific recommendations

5. Implement ModelEditor:
   - Automatically modify network between iterations
   - Add/remove nodes based on recommendations
   - Adjust logic rules for better stability
    """)

def main():
    """
    Main integration test.
    """
    print("🧬 Gene Network Quality Agent - Integration Test")
    print("="*60)
    
    # Test BND integration
    success = test_bnd_integration()
    
    if success:
        print("\n✅ Integration test passed!")
        show_integration_plan()
    else:
        print("\n❌ Integration test failed!")
        return 1
    
    print("\n🎯 Next steps:")
    print("   1. Run: python run_quality_agent.py ../jaya_microc.bnd")
    print("   2. Check generated report in reports/ directory")
    print("   3. Implement full BND integration as outlined above")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
