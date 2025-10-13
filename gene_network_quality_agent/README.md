# 🧬 Gene Network Quality Agent

An iterative, modular system for analyzing Boolean gene regulatory networks (.bnd files) using LangGraph orchestration and integration with `gene_network_standalone.py`.

## 🎯 Overview

The Gene Network Quality Agent performs comprehensive analysis of Boolean gene networks through:

1. **BND File Loading** - Uses `gene_network_standalone.py` for proper .bnd parsing
2. **Topology Analysis** - Network structure, circuits, and feedback loops
3. **Dynamics Simulation** - Attractors, oscillations, and stability
4. **Perturbation Testing** - Knockout and overexpression effects
5. **Biological Validation** - Rule-based pathway validation (LLM-ready)
6. **Iterative Refinement** - Continues until network quality is satisfactory

## 🏗️ Architecture

```
gene_network_quality_agent/
├── agent/                    # Core analysis agents
│   ├── graph.py             # LangGraph workflow definition
│   └── nodes/               # Individual analysis nodes
│       ├── load_model.py    # Load YAML/BND networks
│       ├── topology.py      # Network structure analysis
│       ├── dynamics.py      # Dynamics simulation
│       ├── perturb.py       # Perturbation testing
│       ├── validate.py      # LLM biological validation
│       ├── controller.py    # Iteration control logic
│       └── report.py        # Report generation
├── models/                  # BND network models for testing
│   ├── jaya_microc.bnd     # Large real network (106 nodes)
│   ├── simple_good_network.bnd      # Good p53 pathway
│   ├── feedback_loops_network.bnd   # Problematic feedback loops
│   ├── missing_pathways_network.bnd # Missing biological pathways
│   ├── contradictory_network.bnd    # Contradictory logic
│   └── unstable_network.bnd         # Highly unstable network
├── reports/                 # Generated analysis reports
├── run_quality_agent.py     # Main CLI entry point
└── requirements.txt         # Dependencies
```

## 🚀 Quick Start

1. **Install dependencies:**
```bash
cd gene_network_quality_agent
pip install -r requirements.txt
```

2. **Run analysis on simple good network:**
```bash
python run_quality_agent.py models/simple_good_network.bnd --verbose
```

3. **Test problematic networks:**
```bash
python run_quality_agent.py models/feedback_loops_network.bnd --max-iterations 3
python run_quality_agent.py models/contradictory_network.bnd --max-iterations 2
```

4. **Analyze large real network:**
```bash
python run_quality_agent.py models/jaya_microc.bnd --max-iterations 2
```

## 📊 Output

The agent generates comprehensive YAML reports in the `reports/` directory containing:

- Network structure analysis
- Dynamics and stability assessment  
- Perturbation sensitivity results
- Biological validation scores
- Actionable recommendations
- Iteration history and decision rationale

## 🔧 Current Implementation

This is a **working system** with:
- ✅ Complete LangGraph workflow structure
- ✅ All analysis nodes implemented
- ✅ Full BND file support via `gene_network_standalone.py`
- ✅ Real network topology analysis
- ✅ Dynamics simulation with attractors
- ✅ Perturbation testing (knockout/overexpression)
- ✅ Iterative control logic
- ✅ Comprehensive report generation
- ✅ Multiple test networks with different flaws

**Ready for enhancement:**
- Add real LLM integration for biological validation
- Implement network modification between iterations
- Add more sophisticated dynamics algorithms

## 🧪 Testing

Test different network types:

**Good Network (should converge quickly):**
```bash
python run_quality_agent.py models/simple_good_network.bnd --verbose
```

**Problematic Networks (should iterate multiple times):**
```bash
python run_quality_agent.py models/feedback_loops_network.bnd --max-iterations 3
python run_quality_agent.py models/unstable_network.bnd --max-iterations 2
```

**Large Real Network (106 nodes):**
```bash
python run_quality_agent.py models/jaya_microc.bnd --max-iterations 2
```

## 🔮 Future Extensions

- **ModelEditor**: Automatic network modification between iterations
- **ChatAgent**: Conversational interface for report exploration  
- **RAG Integration**: Validation against public biological databases
