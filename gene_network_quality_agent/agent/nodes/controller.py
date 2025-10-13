"""
Controller Node - Decides whether to continue iteration or stop
"""
from typing import Dict, Any, List


def controller_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Control iteration logic.
    Simple implementation for debugging.
    """
    print("🔄 Controller decision...")
    
    # Get current iteration count
    iterations = state.get("iterations", 0)
    max_iterations = state.get("max_iterations", 3)
    
    # Get analysis results
    validate = state.get("validate", {})
    dynamics = state.get("dynamics", {})
    topology = state.get("topology", {})
    
    # Decision logic
    should_continue = False
    stop_reason = "max_iterations_reached"
    loop_reason = ""
    
    # Check if we've reached max iterations
    if iterations >= max_iterations:
        should_continue = False
        stop_reason = "max_iterations_reached"
        print(f"   ⏹️  Stopping: Maximum iterations ({max_iterations}) reached")
    
    # Check validation score
    elif validate and not validate.get("error"):
        plausibility_score = validate.get("plausibility_score", 0.0)
        issues = validate.get("issues", [])
        
        if plausibility_score >= 0.9 and len(issues) == 0:
            should_continue = False
            stop_reason = "high_quality_achieved"
            print(f"   ✅ Stopping: High quality network achieved (score: {plausibility_score:.2f})")
        
        elif plausibility_score < 0.7:
            should_continue = True
            loop_reason = f"low_plausibility_score_{plausibility_score:.2f}"
            print(f"   🔄 Continuing: Low plausibility score ({plausibility_score:.2f})")

        elif len(issues) > 2:
            should_continue = True
            loop_reason = f"many_issues_{len(issues)}"
            print(f"   🔄 Continuing: Many issues found ({len(issues)})")

        else:
            should_continue = False
            stop_reason = "acceptable_quality"
            print(f"   ✅ Stopping: Acceptable quality (score: {plausibility_score:.2f}, issues: {len(issues)})")
    
    # Check for dynamics issues
    elif dynamics and not dynamics.get("error"):
        unstable_nodes = dynamics.get("unstable_nodes", [])
        has_oscillations = dynamics.get("has_oscillations", False)
        
        if len(unstable_nodes) > 5:
            should_continue = True
            loop_reason = f"too_many_unstable_nodes_{len(unstable_nodes)}"
            print(f"   🔄 Continuing: Too many unstable nodes ({len(unstable_nodes)})")
        
        elif has_oscillations:
            should_continue = True
            loop_reason = "oscillations_detected"
            print(f"   🔄 Continuing: Oscillations detected")
        
        else:
            should_continue = False
            stop_reason = "stable_dynamics"
            print(f"   ✅ Stopping: Stable dynamics achieved")
    
    # Default case
    else:
        should_continue = False
        stop_reason = "no_analysis_available"
        print(f"   ⏹️  Stopping: No analysis results available")
    
    # Update state
    state["should_continue"] = should_continue
    state["stop_reason"] = stop_reason
    state["loop_reason"] = loop_reason
    state["iterations"] = iterations + 1
    
    # Log decision
    print(f"   Decision: {'CONTINUE' if should_continue else 'STOP'}")
    print(f"   Reason: {loop_reason if should_continue else stop_reason}")
    print(f"   Iteration: {state['iterations']}/{max_iterations}")
    
    return state


def evaluate_network_quality(state: Dict[str, Any]) -> float:
    """
    Calculate overall network quality score.
    """
    quality_score = 0.0
    weight_sum = 0.0
    
    # Validation score (weight: 0.5)
    validate = state.get("validate", {})
    if validate and not validate.get("error"):
        plausibility_score = validate.get("plausibility_score", 0.0)
        quality_score += plausibility_score * 0.5
        weight_sum += 0.5
    
    # Dynamics stability (weight: 0.3)
    dynamics = state.get("dynamics", {})
    if dynamics and not dynamics.get("error"):
        unstable_nodes = dynamics.get("unstable_nodes", [])
        has_oscillations = dynamics.get("has_oscillations", False)
        
        # Calculate stability score
        stability_score = 1.0
        if unstable_nodes:
            stability_score -= min(0.5, len(unstable_nodes) * 0.1)
        if has_oscillations:
            stability_score -= 0.3
        
        stability_score = max(0.0, stability_score)
        quality_score += stability_score * 0.3
        weight_sum += 0.3
    
    # Topology quality (weight: 0.2)
    topology = state.get("topology", {})
    if topology and not topology.get("error"):
        cycles = topology.get("cycles", [])
        is_connected = topology.get("is_connected", False)
        
        # Calculate topology score
        topology_score = 0.5 if is_connected else 0.0
        
        # Penalize too many cycles
        if len(cycles) > 10:
            topology_score -= 0.3
        elif len(cycles) > 5:
            topology_score -= 0.1
        
        topology_score = max(0.0, topology_score)
        quality_score += topology_score * 0.2
        weight_sum += 0.2
    
    # Normalize by total weight
    if weight_sum > 0:
        quality_score = quality_score / weight_sum
    
    return quality_score


def should_modify_network(state: Dict[str, Any]) -> bool:
    """
    Determine if network should be modified for next iteration.
    """
    validate = state.get("validate", {})
    
    if validate and not validate.get("error"):
        issues = validate.get("issues", [])
        plausibility_score = validate.get("plausibility_score", 0.0)
        
        # Modify if score is low or many issues
        return plausibility_score < 0.7 or len(issues) > 2
    
    return False


def get_modification_suggestions(state: Dict[str, Any]) -> List[str]:
    """
    Get suggestions for network modifications.
    """
    suggestions = []
    
    validate = state.get("validate", {})
    if validate and not validate.get("error"):
        recommendations = validate.get("recommendations", [])
        suggestions.extend(recommendations)
    
    dynamics = state.get("dynamics", {})
    if dynamics and not dynamics.get("error"):
        unstable_nodes = dynamics.get("unstable_nodes", [])
        if unstable_nodes:
            suggestions.append(f"Stabilize nodes: {', '.join(unstable_nodes[:3])}")
    
    topology = state.get("topology", {})
    if topology and not topology.get("error"):
        cycles = topology.get("cycles", [])
        if len(cycles) > 10:
            suggestions.append("Reduce number of feedback loops")
    
    return suggestions
