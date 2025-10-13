"""
Dynamic Controller - Adaptive analysis pipeline controller
Creates and modifies analysis pipelines at runtime based on available tools and data quality
"""
from typing import Dict, Any, List, Optional
from agent.tool_registry import tool_registry, ToolDefinition


class DynamicController:
    """
    Dynamic controller that creates and adapts analysis pipelines at runtime
    """
    
    def __init__(self):
        self.current_pipeline: List[str] = []
        self.execution_history: List[Dict[str, Any]] = []
        self.quality_thresholds = {
            "plausibility_min": 0.7,
            "max_issues": 2,
            "max_unstable_ratio": 0.3
        }
        self.max_iterations = 5
        self.current_iteration = 0
    
    def create_initial_pipeline(self, available_data: List[str]) -> List[str]:
        """
        Create initial analysis pipeline based on available data and tools
        """
        print("🔧 Creating initial analysis pipeline...")
        
        # Define analysis goals in order of priority
        analysis_goals = [
            "network_loaded",      # Must load the network first
            "topology_analyzed",   # Basic structure analysis
            "dynamics_analyzed",   # Behavior analysis
            "perturbations_tested", # Robustness testing
            "quality_validated",   # Quality assessment
            "report_generated"     # Final reporting
        ]
        
        # Create execution plan
        pipeline = tool_registry.get_execution_plan(analysis_goals, available_data)
        
        print(f"📋 Initial pipeline: {' → '.join(pipeline)}")
        return pipeline
    
    def assess_current_quality(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess current analysis quality and identify issues
        """
        quality_assessment = {
            "overall_score": 0.0,
            "issues": [],
            "recommendations": [],
            "needs_iteration": False
        }
        
        # Check if we have validation results
        if "validation_results" in state:
            validation = state["validation_results"]
            plausibility = validation.get("biological_plausibility", 0.0)
            issues_count = len(validation.get("issues", []))
            
            quality_assessment["overall_score"] = plausibility
            quality_assessment["issues"] = validation.get("issues", [])
            
            # Determine if iteration is needed
            if plausibility < self.quality_thresholds["plausibility_min"]:
                quality_assessment["needs_iteration"] = True
                quality_assessment["recommendations"].append(
                    f"Low biological plausibility ({plausibility:.2f})"
                )
            
            if issues_count > self.quality_thresholds["max_issues"]:
                quality_assessment["needs_iteration"] = True
                quality_assessment["recommendations"].append(
                    f"Too many issues found ({issues_count})"
                )
        
        # Check dynamics results
        if "dynamics_results" in state:
            dynamics = state["dynamics_results"]
            total_nodes = len(state.get("model_data", {}).get("nodes", {}))
            unstable_count = len(dynamics.get("unstable_nodes", []))
            
            if total_nodes > 0:
                unstable_ratio = unstable_count / total_nodes
                if unstable_ratio > self.quality_thresholds["max_unstable_ratio"]:
                    quality_assessment["needs_iteration"] = True
                    quality_assessment["recommendations"].append(
                        f"High instability ratio ({unstable_ratio:.2f})"
                    )
        
        return quality_assessment
    
    def adapt_pipeline(self, state: Dict[str, Any], quality_assessment: Dict[str, Any]) -> List[str]:
        """
        Adapt the pipeline based on current state and quality assessment
        """
        print("🔄 Adapting pipeline based on current analysis...")
        
        # Start with available data from current state
        available_data = list(state.keys())
        
        # Determine what additional analysis is needed
        additional_goals = []
        
        # If topology issues, add more topology analysis
        if any("topology" in issue.lower() for issue in quality_assessment["issues"]):
            additional_goals.append("topology_deep_analyzed")
        
        # If dynamics issues, add more dynamics analysis
        if any("dynamic" in issue.lower() or "unstable" in issue.lower() 
               for issue in quality_assessment["issues"]):
            additional_goals.append("dynamics_deep_analyzed")
        
        # If biological issues, add more validation
        if any("biological" in issue.lower() or "pathway" in issue.lower() 
               for issue in quality_assessment["issues"]):
            additional_goals.append("biology_deep_validated")
        
        # Always end with quality assessment and reporting
        additional_goals.extend(["quality_validated", "report_generated"])
        
        # Create adapted pipeline
        adapted_pipeline = tool_registry.get_execution_plan(additional_goals, available_data)
        
        print(f"🔄 Adapted pipeline: {' → '.join(adapted_pipeline)}")
        return adapted_pipeline
    
    def should_continue_iteration(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decide whether to continue iterating or stop
        """
        self.current_iteration += 1
        
        # Assess current quality
        quality_assessment = self.assess_current_quality(state)
        
        decision = {
            "action": "STOP",
            "reason": "acceptable_quality",
            "quality_assessment": quality_assessment,
            "iteration": self.current_iteration
        }
        
        # Check stopping conditions
        if self.current_iteration >= self.max_iterations:
            decision["action"] = "STOP"
            decision["reason"] = f"max_iterations_reached_{self.max_iterations}"
        elif quality_assessment["needs_iteration"]:
            decision["action"] = "CONTINUE"
            decision["reason"] = "quality_issues_detected"
            # Create adapted pipeline for next iteration
            decision["next_pipeline"] = self.adapt_pipeline(state, quality_assessment)
        
        print(f"🎯 Controller decision: {decision['action']} - {decision['reason']}")
        
        # Store execution history
        self.execution_history.append({
            "iteration": self.current_iteration,
            "decision": decision["action"],
            "reason": decision["reason"],
            "quality_score": quality_assessment["overall_score"],
            "issues_count": len(quality_assessment["issues"]),
            "pipeline": self.current_pipeline.copy()
        })
        
        return decision
    
    def execute_pipeline_step(self, step_name: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single pipeline step using the tool registry
        """
        print(f"🔄 Executing step: {step_name}")
        
        tool = tool_registry.get_tool(step_name)
        if not tool:
            print(f"❌ Tool not found: {step_name}")
            return state
        
        if not tool_registry.can_execute_tool(step_name, list(state.keys())):
            print(f"❌ Cannot execute {step_name}: missing requirements {tool.input_requirements}")
            return state
        
        try:
            # Execute the tool function
            result = tool.function(state)
            
            # Update state with results
            if isinstance(result, dict):
                state.update(result)
            
            print(f"✅ Completed step: {step_name}")
            return state
            
        except Exception as e:
            print(f"❌ Error executing {step_name}: {e}")
            return state
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get summary of execution history
        """
        return {
            "total_iterations": self.current_iteration,
            "execution_history": self.execution_history,
            "final_pipeline": self.current_pipeline,
            "quality_thresholds": self.quality_thresholds
        }


def dynamic_controller_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for dynamic controller
    """
    controller = state.get("controller")
    if not controller:
        controller = DynamicController()
        state["controller"] = controller
    
    # Make control decision
    decision = controller.should_continue_iteration(state)
    
    # Update state with decision
    state["controller_decision"] = decision
    state["iteration"] = decision["iteration"]
    
    return state
