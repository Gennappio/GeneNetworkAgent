# 🧬 Gene Network Quality Agent

A production-ready tool for gene network analysis with AI-powered insights using OpenAI's GPT-3.5 Turbo.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation
```bash
pip install openai networkx pyyaml
```

### Setup
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Basic Usage
```bash
# Run analysis pipeline
python gene_agent.py models/simple_good_network.bnd --default-pipeline

# Get AI-powered insights
python gene_agent.py --refine reports/analysis_report_TIMESTAMP.yaml --summarize "therapeutic targets"

# Ask specific questions
python gene_agent.py --refine reports/analysis_report_TIMESTAMP.yaml --ask "What are the key regulatory hubs?"
```

## 📋 Features

### Core Analysis Pipeline
- **Network Loading**: Parse .bnd Boolean network files
- **Topology Analysis**: Network structure and connectivity
- **Dynamics Analysis**: Attractor identification and stability
- **Perturbation Testing**: Knockout and overexpression experiments
- **Biological Validation**: AI-powered plausibility assessment

### AI-Powered Insights
- **Expert Analysis**: GPT-3.5 powered biological interpretation
- **Research Summaries**: Publication-ready reports for biologists
- **Interactive Q&A**: Ask specific questions about your network
- **Tool Recommendations**: AI suggests additional analyses

## 🔧 CLI Reference

### Modes

#### `--default-pipeline`
Run standard analysis pipeline and generate structured reports.
```bash
python gene_agent.py network.bnd --default-pipeline [--verbose]
```

#### `--refine`
Use AI to review and enhance existing analysis.
```bash
python gene_agent.py --refine report.yaml [--model gpt-3.5-turbo] [--verbose]
```

#### `--ask`
Ask specific questions about your analysis.
```bash
python gene_agent.py --refine report.yaml --ask "What are the therapeutic targets?" [--model gpt-3.5-turbo]
```

#### `--summarize`
Generate biologist-friendly summaries with domain focus.
```bash
python gene_agent.py --refine report.yaml --summarize "drug discovery" [--model gpt-3.5-turbo]
```

### Options
- `--model`: AI model to use (default: gpt-3.5-turbo)
- `--verbose`: Enable detailed logging
- `--help`: Show usage information

## 📊 Output Formats

### Technical Reports (YAML)
Structured reports for programmatic analysis:
```yaml
metadata:
  timestamp: "20251014_231624"
  network_name: "Simple Good Network"
  analysis_type: "default_pipeline"

quality_metrics:
  biological_plausibility: 0.54
  issues_found: 3
  overall_quality: 0.0

topology_analysis:
  nodes: 9
  edges: 0
  connected: false
```

### Biologist Summaries (Markdown)
Publication-ready reports for researchers:
```markdown
# Gene Network Analysis: Therapeutic Target Identification

## Key Findings
- p53 acts as central regulatory hub
- Network exhibits oscillatory behavior
- Multiple therapeutic intervention points identified

## Therapeutic Targets
1. **p53** - Central tumor suppressor
2. **MDM2** - p53 negative regulator
3. **BCL2** - Anti-apoptotic protein
```

## 🏗️ Architecture

### Clean, Production-Ready Design
- **No Legacy Code**: Removed all dynamic architecture complexity
- **No Mock Functions**: Real AI integration only
- **Minimal Dependencies**: Core functionality with essential tools
- **Error Handling**: Proper exception handling and logging

### Core Components
```
gene_agent.py           # Main CLI application
agent/tools/            # Analysis tools
├── load_bnd_network.py
├── analyze_topology.py
├── analyze_dynamics.py
├── test_perturbations.py
└── validate_biology.py
models/                 # Example BND networks
reports/                # Generated analysis reports
```

## 🔒 Security

- **Environment Variables**: API keys via OPENAI_API_KEY
- **No Hardcoded Secrets**: Clean, secure codebase
- **Input Validation**: Proper error handling
- **Production Ready**: Suitable for deployment

## 📈 Use Cases

### Research Applications
- **Cancer Research**: Identify therapeutic targets and drug mechanisms
- **Systems Biology**: Understand network dynamics and regulation
- **Drug Discovery**: Find intervention points and combination strategies
- **Pathway Analysis**: Validate biological coherence and completeness

### Technical Applications
- **Network Validation**: Assess model quality and biological plausibility
- **Comparative Analysis**: Compare different network models
- **Hypothesis Generation**: AI-powered insights for further research
- **Report Generation**: Automated documentation for research workflows

## 🎯 Example Workflow

```bash
# 1. Analyze network
python gene_agent.py models/simple_good_network.bnd --default-pipeline
# → reports/analysis_report_20251014_231624.yaml

# 2. Get AI insights
python gene_agent.py --refine reports/analysis_report_20251014_231624.yaml
# → AI recommendations for additional analysis

# 3. Ask research questions
python gene_agent.py --refine reports/analysis_report_20251014_231624.yaml \
  --ask "What are the most promising therapeutic targets?"
# → Expert AI analysis of therapeutic opportunities

# 4. Generate research summary
python gene_agent.py --refine reports/analysis_report_20251014_231624.yaml \
  --summarize "cancer therapeutics"
# → reports/analysis_report_20251014_231624_biologist_summary_cancer_therapeutics.md
```

## 🚀 Production Deployment

### Requirements
- OpenAI API key with sufficient quota
- Python 3.8+ environment
- Network access for API calls

### Recommendations
- **Rate Limiting**: Implement for high-volume use
- **Caching**: Cache AI responses to reduce costs
- **Monitoring**: Track API usage and costs
- **Scaling**: Consider load balancing for multiple users

## 📞 Support

### Documentation
- `--help`: CLI usage and examples
- `NEW_ARCHITECTURE.md`: Complete architecture overview
- `SETUP.md`: Detailed setup instructions
- `REAL_LLM_TEST_RESULTS.md`: Testing documentation

### Example Networks
- `models/simple_good_network.bnd`: Well-structured p53 pathway
- `models/unstable_network.bnd`: Network with stability issues
- `models/feedback_loops_network.bnd`: Complex regulatory circuits

**Ready for production use with real AI-powered biological analysis!** 🧬✨
