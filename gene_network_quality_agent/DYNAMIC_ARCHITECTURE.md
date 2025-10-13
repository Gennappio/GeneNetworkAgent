# 🏗️ Dynamic Architecture - Gene Network Quality Agent

## 🎯 Overview

The Gene Network Quality Agent now features a **dynamic, non-hardcoded architecture** that:

- **Discovers tools at runtime** from the `agent/tools/` directory
- **Creates adaptive analysis pipelines** based on available tools and data quality
- **Supports MCP-style tool registration** with metadata and capabilities
- **Adapts execution flow** based on quality assessment and iteration needs
- **Allows runtime tool addition** without code changes to the core system

## 🔧 Core Components

### 1. **Tool Registry** (`agent/tool_registry.py`)

The central registry that manages all analysis tools:

```python
from agent.tool_registry import tool_registry, ToolDefinition

# Discover tools automatically
tool_registry.discover_tools()

# Register custom tools at runtime
custom_tool = ToolDefinition(
    name="my_custom_analysis",
    description="Custom analysis for specific needs",
    function=my_analysis_function,
    input_requirements=["model_data"],
    output_provides=["custom_results"],
    category="analyzer",
    priority=75
)
tool_registry.register_tool(custom_tool)
```

**Key Features:**
- ✅ **Automatic tool discovery** from file system
- ✅ **MCP-style metadata** (inputs, outputs, categories, priorities)
- ✅ **Dependency resolution** and execution planning
- ✅ **Runtime tool registration** for extensibility

### 2. **Dynamic Controller** (`agent/dynamic_controller.py`)

Intelligent controller that creates and adapts pipelines:

```python
from agent.dynamic_controller import DynamicController

controller = DynamicController()

# Create initial pipeline based on goals
pipeline = controller.create_initial_pipeline(available_data)

# Assess quality and decide next steps
quality_assessment = controller.assess_current_quality(state)
decision = controller.should_continue_iteration(state)

# Adapt pipeline based on issues found
if decision["action"] == "CONTINUE":
    adapted_pipeline = controller.adapt_pipeline(state, quality_assessment)
```

**Key Features:**
- ✅ **Goal-driven pipeline creation** 
- ✅ **Quality-based adaptation** 
- ✅ **Iteration control** with configurable thresholds
- ✅ **Execution history tracking**

### 3. **Dynamic Graph** (`agent/dynamic_graph.py`)

LangGraph workflow that adapts at runtime:

```python
from agent.dynamic_graph import run_dynamic_analysis

# Run analysis with automatic tool discovery and adaptation
result = run_dynamic_analysis(
    model_path="models/network.bnd",
    max_iterations=3,
    verbose=True
)
```

**Key Features:**
- ✅ **Runtime graph construction** based on available tools
- ✅ **Adaptive execution flow** 
- ✅ **Tool-agnostic pipeline execution**

## 🛠️ Tool Development

### Creating New Tools

Tools are Python files in `agent/tools/` with this structure:

```python
# agent/tools/my_new_tool.py

def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main tool function - receives state, returns updated state
    """
    # Your analysis logic here
    results = perform_analysis(state)
    
    return {
        "my_results": results,
        "my_analysis_complete": True
    }

# Tool metadata for registry
TOOL_DEFINITION = {
    "name": "my_new_tool",
    "description": "Description of what this tool does",
    "function_name": "execute",  # Function to call
    "input_requirements": ["model_data"],  # What data it needs
    "output_provides": ["my_results", "my_analysis_complete"],  # What it produces
    "category": "analyzer",  # Tool category
    "priority": 75,  # Execution priority (higher = more important)
    "enabled": True  # Whether tool is active
}
```

### Tool Categories

- **`loader`**: Data loading and parsing tools
- **`analyzer`**: Network analysis tools
- **`validator`**: Validation and quality assessment tools  
- **`reporter`**: Report generation tools
- **`controller`**: Control flow and decision tools

### MCP-Style Capabilities

Each tool declares its capabilities:

```python
TOOL_DEFINITION = {
    "input_requirements": ["model_data", "topology_results"],  # What it needs
    "output_provides": ["deep_analysis", "enhanced_topology"],  # What it produces
    "priority": 85,  # Higher priority tools run first
    "category": "analyzer"  # Logical grouping
}
```

## 🔄 Adaptive Pipeline Creation

### Goal-Driven Planning

The system creates pipelines to achieve specific goals:

```python
# Define what you want to achieve
goals = [
    "network_loaded",
    "topology_analyzed", 
    "dynamics_analyzed",
    "quality_validated",
    "report_generated"
]

# System automatically creates execution plan
pipeline = tool_registry.get_execution_plan(goals, available_data)
# Result: ["load_bnd_network", "analyze_topology", "analyze_dynamics", "validate_biology", "generate_report"]
```

### Quality-Driven Adaptation

The controller adapts pipelines based on analysis quality:

```python
# Low biological plausibility → Add more validation
if plausibility < 0.7:
    adapted_pipeline.extend(["pathway_validator", "validate_biology"])

# Many unstable nodes → Add deeper dynamics analysis  
if unstable_ratio > 0.3:
    adapted_pipeline.extend(["deep_dynamics_analysis"])

# Topology issues → Add advanced topology analysis
if "topology" in issues:
    adapted_pipeline.extend(["deep_topology_analysis"])
```

## 🚀 Usage Examples

### 1. Basic Analysis

```bash
python run_dynamic_agent.py models/network.bnd --max-iterations 3
```

### 2. Adding Custom Tools at Runtime

```python
# Create custom tool
def metabolic_analysis(state):
    # Custom analysis logic
    return {"metabolic_results": results}

# Register it
tool_registry.register_tool(ToolDefinition(
    name="metabolic_analysis",
    function=metabolic_analysis,
    input_requirements=["model_data"],
    output_provides=["metabolic_results"],
    category="analyzer"
))

# System automatically includes it in future pipelines
```

### 3. Demonstrating Architecture

```bash
python demo_dynamic_tools.py
```

This shows:
- Runtime tool discovery and registration
- Adaptive pipeline creation for different scenarios
- MCP-style tool metadata and capabilities
- Quality-driven pipeline adaptation

## 🎯 Key Benefits

### ✅ **Non-Hardcoded Controller**
- Controller creates pipelines dynamically based on available tools
- No hardcoded analysis sequences
- Adapts to new tools automatically

### ✅ **Runtime Extensibility**
- Add new tools by dropping files in `agent/tools/`
- Register tools programmatically at runtime
- No core system changes needed

### ✅ **MCP-Style Architecture**
- Tools declare capabilities and requirements
- Automatic dependency resolution
- Standardized tool interface

### ✅ **Quality-Driven Adaptation**
- Pipelines adapt based on analysis results
- Intelligent iteration control
- Goal-oriented execution planning

### ✅ **Simple Tool Development**
- Minimal boilerplate for new tools
- Clear separation of concerns
- Easy debugging and testing

## 🔮 Future Enhancements

The architecture is ready for:

1. **LLM Integration**: Tools can easily integrate LLMs for validation
2. **Network Modification**: Tools can modify networks between iterations
3. **External Tool Integration**: Support for external analysis tools
4. **Distributed Execution**: Tools can run on different machines
5. **Interactive Analysis**: Web interface for tool selection and configuration

## 📊 Architecture Comparison

| Feature | Old System | New Dynamic System |
|---------|------------|-------------------|
| Pipeline Creation | Hardcoded sequence | Goal-driven, adaptive |
| Tool Addition | Code changes required | Drop file in directory |
| Controller Logic | Fixed thresholds | Quality-driven adaptation |
| Tool Discovery | Manual registration | Automatic discovery |
| Extensibility | Limited | MCP-style, unlimited |
| Debugging | Monolithic | Modular, tool-by-tool |

The new architecture transforms the system from a **rigid, hardcoded pipeline** into a **flexible, adaptive, and extensible analysis framework** that can grow and adapt to new requirements without core system changes.
