#!/usr/bin/env python3
"""
Demo: Dynamic Tool Addition and MCP-style Architecture
Shows how to add new tools at runtime and create adaptive pipelines
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.tool_registry import tool_registry, ToolDefinition
from agent.dynamic_controller import DynamicController
from typing import Dict, Any


def demo_runtime_tool_addition():
    """
    Demonstrate adding tools at runtime
    """
    print("🔧 DEMO: Runtime Tool Addition")
    print("=" * 50)
    
    # Discover existing tools
    print("1. Discovering existing tools...")
    tool_registry.discover_tools()
    
    print(f"   Found {len(tool_registry.tools)} tools")
    for category, tools in tool_registry.list_tools().items():
        print(f"   {category}: {len(tools)} tools")
    
    print("\n2. Adding custom tool at runtime...")
    
    # Define a custom analysis tool
    def custom_metabolic_analysis(state: Dict[str, Any]) -> Dict[str, Any]:
        """Custom metabolic pathway analysis"""
        print("🔄 Running custom metabolic analysis...")
        
        model_data = state.get("model_data", {})
        nodes = model_data.get("nodes", {})
        
        # Look for metabolic nodes
        metabolic_nodes = []
        metabolic_keywords = ["ATP", "glucose", "lactate", "pyruvate", "glyco", "mito"]
        
        for node_name in nodes.keys():
            if any(keyword.lower() in node_name.lower() for keyword in metabolic_keywords):
                metabolic_nodes.append(node_name)
        
        results = {
            "metabolic_nodes_found": metabolic_nodes,
            "metabolic_node_count": len(metabolic_nodes),
            "has_glycolysis": any("glyco" in node.lower() for node in metabolic_nodes),
            "has_mitochondrial": any("mito" in node.lower() for node in metabolic_nodes),
            "metabolic_score": len(metabolic_nodes) / max(len(nodes), 1)
        }
        
        print(f"   Found {len(metabolic_nodes)} metabolic nodes")
        print(f"   Metabolic score: {results['metabolic_score']:.2f}")
        
        return {
            "metabolic_analysis_results": results,
            "metabolic_analyzed": True
        }
    
    # Create tool definition
    custom_tool = ToolDefinition(
        name="custom_metabolic_analysis",
        description="Analyze metabolic pathways and energy production",
        function=custom_metabolic_analysis,
        input_requirements=["model_data"],
        output_provides=["metabolic_analysis_results", "metabolic_analyzed"],
        category="analyzer",
        priority=65,
        enabled=True
    )
    
    # Register the tool
    tool_registry.register_tool(custom_tool)
    
    print(f"   ✅ Custom tool registered: {custom_tool.name}")
    print(f"   Total tools now: {len(tool_registry.tools)}")
    
    return custom_tool


def demo_adaptive_pipeline():
    """
    Demonstrate adaptive pipeline creation
    """
    print("\n🔄 DEMO: Adaptive Pipeline Creation")
    print("=" * 50)
    
    controller = DynamicController()
    
    # Simulate different analysis scenarios
    scenarios = [
        {
            "name": "Basic Analysis",
            "available_data": ["model_path"],
            "goals": ["network_loaded", "topology_analyzed", "report_generated"]
        },
        {
            "name": "Deep Analysis", 
            "available_data": ["model_path"],
            "goals": ["network_loaded", "topology_analyzed", "topology_deep_analyzed", 
                     "dynamics_analyzed", "perturbations_tested", "quality_validated", "report_generated"]
        },
        {
            "name": "Metabolic Focus",
            "available_data": ["model_path"],
            "goals": ["network_loaded", "metabolic_analyzed", "biology_deep_validated", "report_generated"]
        },
        {
            "name": "Continuing Analysis",
            "available_data": ["model_data", "topology_results", "dynamics_results"],
            "goals": ["topology_deep_analyzed", "biology_deep_validated", "report_generated"]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Scenario: {scenario['name']}")
        print(f"   Available data: {scenario['available_data']}")
        print(f"   Goals: {scenario['goals']}")
        
        # Create execution plan
        pipeline = tool_registry.get_execution_plan(scenario['goals'], scenario['available_data'])
        
        print(f"   📋 Generated pipeline: {' → '.join(pipeline)}")
        
        # Show which tools can be executed immediately
        executable_tools = []
        for tool_name in pipeline:
            if tool_registry.can_execute_tool(tool_name, scenario['available_data']):
                executable_tools.append(tool_name)
        
        print(f"   ✅ Immediately executable: {executable_tools}")


def demo_mcp_style_tool_discovery():
    """
    Demonstrate MCP-style tool discovery and metadata
    """
    print("\n🔍 DEMO: MCP-Style Tool Discovery")
    print("=" * 50)
    
    print("1. Tool Categories and Capabilities:")
    for category, description in tool_registry.categories.items():
        tools = tool_registry.get_tools_by_category(category)
        print(f"\n   📂 {category.upper()}: {description}")
        
        for tool in tools:
            print(f"      🔧 {tool.name}")
            print(f"         Description: {tool.description}")
            print(f"         Inputs: {tool.input_requirements}")
            print(f"         Outputs: {tool.output_provides}")
            print(f"         Priority: {tool.priority}")
    
    print("\n2. Tool Dependency Analysis:")
    
    # Show which tools can provide specific outputs
    important_outputs = ["network_loaded", "topology_analyzed", "dynamics_analyzed", 
                        "quality_validated", "report_generated"]
    
    for output in important_outputs:
        providers = tool_registry.find_tools_for_requirements([output])
        print(f"\n   📤 '{output}' can be provided by:")
        for tool in providers:
            print(f"      - {tool.name} (priority: {tool.priority})")
    
    print("\n3. Tool Execution Requirements:")
    
    # Show what each tool needs to run
    for tool_name, tool_def in tool_registry.tools.items():
        if tool_def.input_requirements:
            print(f"\n   🔧 {tool_name} requires:")
            for req in tool_def.input_requirements:
                providers = tool_registry.find_tools_for_requirements([req])
                provider_names = [p.name for p in providers]
                print(f"      - {req} (from: {', '.join(provider_names) if provider_names else 'external'})")


def demo_quality_driven_adaptation():
    """
    Demonstrate how the controller adapts based on quality assessment
    """
    print("\n🎯 DEMO: Quality-Driven Pipeline Adaptation")
    print("=" * 50)
    
    controller = DynamicController()
    
    # Simulate different quality scenarios
    quality_scenarios = [
        {
            "name": "High Quality Network",
            "validation_results": {
                "biological_plausibility": 0.85,
                "issues": ["Minor optimization possible"]
            },
            "dynamics_results": {
                "unstable_nodes": ["node1"]
            }
        },
        {
            "name": "Low Quality Network",
            "validation_results": {
                "biological_plausibility": 0.45,
                "issues": ["Missing p53 pathway", "No apoptosis control", "Contradictory logic"]
            },
            "dynamics_results": {
                "unstable_nodes": ["node1", "node2", "node3", "node4", "node5"]
            }
        },
        {
            "name": "Topology Issues",
            "validation_results": {
                "biological_plausibility": 0.75,
                "issues": ["Complex topology detected", "Many feedback loops"]
            },
            "dynamics_results": {
                "unstable_nodes": ["node1", "node2"]
            }
        }
    ]
    
    for i, scenario in enumerate(quality_scenarios, 1):
        print(f"\n{i}. Scenario: {scenario['name']}")
        
        # Create mock state
        state = {
            "model_data": {"nodes": {f"node{j}": {} for j in range(1, 11)}},
            "validation_results": scenario["validation_results"],
            "dynamics_results": scenario["dynamics_results"]
        }
        
        # Assess quality
        quality_assessment = controller.assess_current_quality(state)
        
        print(f"   Quality Score: {quality_assessment['overall_score']:.2f}")
        print(f"   Issues: {len(quality_assessment['issues'])}")
        print(f"   Needs Iteration: {quality_assessment['needs_iteration']}")
        
        if quality_assessment["needs_iteration"]:
            # Generate adapted pipeline
            adapted_pipeline = controller.adapt_pipeline(state, quality_assessment)
            print(f"   📋 Adapted Pipeline: {' → '.join(adapted_pipeline)}")
        else:
            print("   ✅ Quality acceptable - no adaptation needed")


def main():
    """
    Run all demonstrations
    """
    print("🧬 Dynamic Gene Network Quality Agent - Tool Architecture Demo")
    print("=" * 70)
    
    # Demo 1: Runtime tool addition
    custom_tool = demo_runtime_tool_addition()
    
    # Demo 2: Adaptive pipeline creation
    demo_adaptive_pipeline()
    
    # Demo 3: MCP-style tool discovery
    demo_mcp_style_tool_discovery()
    
    # Demo 4: Quality-driven adaptation
    demo_quality_driven_adaptation()
    
    print("\n" + "=" * 70)
    print("🎉 All demonstrations completed!")
    print("\nKey Features Demonstrated:")
    print("✅ Runtime tool registration and discovery")
    print("✅ MCP-style tool metadata and capabilities")
    print("✅ Adaptive pipeline generation based on goals")
    print("✅ Quality-driven pipeline adaptation")
    print("✅ Dependency resolution and execution planning")
    print("\n🚀 The system is ready for production enhancement!")


if __name__ == "__main__":
    main()
