#!/usr/bin/env python3
"""
Gene Network Quality Agent - Main Entry Point

This script runs the complete gene network quality analysis using LangGraph.
It analyzes network topology, dynamics, perturbations, and biological validity.

Usage:
    python run_quality_agent.py models/example_network.yaml
    python run_quality_agent.py path/to/network.bnd --max-iterations 5
"""

import argparse
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent.graph import run_quality_analysis


def main():
    """
    Main entry point for the Gene Network Quality Agent.
    """
    parser = argparse.ArgumentParser(
        description='Gene Network Quality Agent - Iterative network analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_quality_agent.py models/example_network.yaml
    python run_quality_agent.py jaya_microc.bnd --max-iterations 5
    python run_quality_agent.py network.yaml --max-iterations 2

The agent will:
1. Load the gene network model
2. Analyze topology (circuits, feedback loops)
3. Simulate dynamics (attractors, stability)
4. Test perturbations (knockouts, overexpression)
5. Validate biological plausibility
6. Generate comprehensive report

Results are saved in the 'reports/' directory.
        """
    )
    
    parser.add_argument(
        'model_path',
        help='Path to gene network model file (YAML or BND format)'
    )
    
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=3,
        help='Maximum number of analysis iterations (default: 3)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.model_path):
        print(f"❌ Error: Model file not found: {args.model_path}")
        print(f"   Please check the file path and try again.")
        return 1
    
    # Check file extension
    file_ext = Path(args.model_path).suffix.lower()
    if file_ext not in ['.yaml', '.yml', '.bnd']:
        print(f"❌ Error: Unsupported file format: {file_ext}")
        print(f"   Supported formats: .yaml, .yml, .bnd")
        return 1
    
    # Print banner
    print("🧬 Gene Network Quality Agent")
    print("="*50)
    print(f"📁 Model file: {args.model_path}")
    print(f"🔄 Max iterations: {args.max_iterations}")
    print(f"📊 Verbose mode: {'ON' if args.verbose else 'OFF'}")
    print("="*50)
    
    try:
        # Run the analysis
        result = run_quality_analysis(
            model_path=args.model_path,
            max_iterations=args.max_iterations
        )
        
        # Check for errors
        if result.get("error"):
            print(f"\n❌ Analysis failed with error:")
            print(f"   {result['error']}")
            return 1
        
        # Success message
        print(f"\n🎉 Analysis completed successfully!")
        
        # Show report location
        report_path = result.get("report_path", "")
        if report_path:
            print(f"📄 Report saved to: {report_path}")
            
            # Show quick summary if verbose
            if args.verbose:
                print_verbose_summary(result)
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Analysis interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n❌ Unexpected error during analysis:")
        print(f"   {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def print_verbose_summary(result: dict):
    """
    Print detailed summary of analysis results.
    """
    print(f"\n📊 DETAILED SUMMARY")
    print("="*40)
    
    # Model info
    model = result.get("model", {})
    if model:
        print(f"Network name: {model.get('name', 'Unknown')}")
        print(f"Description: {model.get('description', 'No description')}")
        nodes = model.get("nodes", {})
        print(f"Total nodes: {len(nodes)}")
    
    # Topology
    topology = result.get("topology", {})
    if topology and not topology.get("error"):
        print(f"\n🔗 Topology Analysis:")
        print(f"  Edges: {topology.get('edge_count', 0)}")
        print(f"  Density: {topology.get('density', 0.0):.3f}")
        print(f"  Connected: {topology.get('is_connected', False)}")
        print(f"  Feedback loops: {len(topology.get('cycles', []))}")
    
    # Dynamics
    dynamics = result.get("dynamics", {})
    if dynamics and not dynamics.get("error"):
        print(f"\n⚡ Dynamics Analysis:")
        print(f"  Attractors: {len(dynamics.get('attractors', []))}")
        print(f"  Unstable nodes: {dynamics.get('unstable_nodes', [])}")
        print(f"  Oscillations: {dynamics.get('has_oscillations', False)}")
    
    # Perturbations
    perturb = result.get("perturb", {})
    if perturb and not perturb.get("error"):
        print(f"\n🧪 Perturbation Analysis:")
        print(f"  Robust nodes: {perturb.get('robust_nodes', [])}")
        print(f"  Sensitive nodes: {perturb.get('sensitive_nodes', [])}")
    
    # Validation
    validate = result.get("validate", {})
    if validate and not validate.get("error"):
        print(f"\n🔬 Biological Validation:")
        print(f"  Plausibility score: {validate.get('plausibility_score', 0.0):.2f}")
        issues = validate.get('issues', [])
        print(f"  Issues found: {len(issues)}")
        if issues:
            for issue in issues[:3]:  # Show first 3 issues
                print(f"    - {issue}")
            if len(issues) > 3:
                print(f"    ... and {len(issues) - 3} more")
    
    # Control flow
    print(f"\n🎯 Analysis Control:")
    print(f"  Iterations completed: {result.get('iterations', 0)}")
    print(f"  Stop reason: {result.get('stop_reason', 'unknown')}")
    if result.get('loop_reason'):
        print(f"  Loop reason: {result.get('loop_reason')}")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
