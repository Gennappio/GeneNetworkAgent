#!/usr/bin/env python3
"""
Dynamic Gene Network Quality Agent - Main CLI
Uses the new dynamic tool registry system
"""
import argparse
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.dynamic_graph import run_dynamic_analysis


def main():
    parser = argparse.ArgumentParser(
        description="Dynamic Gene Network Quality Agent - Adaptive analysis with tool registry"
    )
    parser.add_argument(
        "model_path",
        help="Path to the BND gene network file"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum number of analysis iterations (default: 3)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate model file exists
    if not Path(args.model_path).exists():
        print(f"❌ Error: Model file not found: {args.model_path}")
        print("   Please check the file path and try again.")
        sys.exit(1)
    
    # Print header
    print("🧬 Dynamic Gene Network Quality Agent")
    print("=" * 50)
    print(f"📁 Model file: {args.model_path}")
    print(f"🔄 Max iterations: {args.max_iterations}")
    print(f"📊 Verbose mode: {'ON' if args.verbose else 'OFF'}")
    print("=" * 50)
    
    try:
        # Run dynamic analysis
        result = run_dynamic_analysis(
            model_path=args.model_path,
            max_iterations=args.max_iterations,
            verbose=args.verbose
        )
        
        # Print summary
        print_analysis_summary(result)
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def print_analysis_summary(result: dict):
    """Print analysis summary"""
    print("\n📊 DYNAMIC ANALYSIS SUMMARY")
    print("=" * 40)
    
    # Basic info
    network_name = result.get("network_name", "Unknown")
    iterations = result.get("iteration", 1)
    
    print(f"Network: {network_name}")
    print(f"Iterations: {iterations}")
    
    # Controller decision
    controller_decision = result.get("controller_decision", {})
    stop_reason = controller_decision.get("reason", "unknown")
    print(f"Stop reason: {stop_reason}")
    
    # Quality metrics
    validation_results = result.get("validation_results", {})
    if validation_results:
        plausibility = validation_results.get("biological_plausibility", 0.0)
        issues = len(validation_results.get("issues", []))
        print(f"Biological plausibility: {plausibility:.2f}")
        print(f"Issues found: {issues}")
    
    # Dynamics info
    dynamics_results = result.get("dynamics_results", {})
    if dynamics_results:
        unstable_nodes = len(dynamics_results.get("unstable_nodes", []))
        oscillations = dynamics_results.get("has_oscillations", False)
        print(f"Unstable nodes: {unstable_nodes}")
        print(f"Oscillations: {'Yes' if oscillations else 'No'}")
    
    # Perturbation info
    perturbation_results = result.get("perturbation_results", {})
    if perturbation_results:
        robust_nodes = len(perturbation_results.get("robust_nodes", []))
        sensitive_nodes = len(perturbation_results.get("sensitive_nodes", []))
        print(f"Robust nodes: {robust_nodes}")
        print(f"Sensitive nodes: {sensitive_nodes}")
    
    # Report file
    report_file = result.get("report_file")
    if report_file:
        print(f"Report saved: {report_file}")
    
    print("\n🎉 Dynamic analysis completed successfully!")
    if report_file:
        print(f"📄 Report saved to: {report_file}")
    
    # Tool registry summary
    controller = result.get("controller")
    if controller:
        execution_summary = controller.get_execution_summary()
        print(f"\n🔧 EXECUTION SUMMARY")
        print("=" * 40)
        print(f"Total iterations: {execution_summary.get('total_iterations', 0)}")
        
        history = execution_summary.get("execution_history", [])
        if history:
            print("Iteration history:")
            for entry in history:
                iteration = entry.get("iteration", 0)
                decision = entry.get("decision", "unknown")
                quality = entry.get("quality_score", 0.0)
                print(f"  {iteration}: {decision} (quality: {quality:.2f})")


if __name__ == "__main__":
    main()
