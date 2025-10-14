# 🚀 Gene Agent Setup Guide

## 📋 **Prerequisites**

### **Python Environment**
- Python 3.8+
- Required packages: `openai`, `networkx`, `pyyaml`, `pathlib`

### **Install Dependencies**
```bash
pip install openai networkx pyyaml
```

## 🔑 **OpenAI API Setup**

### **Option 1: Environment Variable (Recommended)**
```bash
# Set environment variable
export OPENAI_API_KEY="your-openai-api-key-here"

# Or add to your shell profile (.bashrc, .zshrc, etc.)
echo 'export OPENAI_API_KEY="your-openai-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### **Option 2: Mock Responses (Demo Mode)**
If no API key is provided, the system automatically uses mock responses for demonstration:
```bash
# No API key needed - uses mock responses
python gene_agent.py models/simple_good_network.bnd --default-pipeline
```

## 🧪 **Quick Start**

### **1. Run Default Analysis**
```bash
python gene_agent.py models/simple_good_network.bnd --default-pipeline --verbose
```

### **2. Refine with LLM**
```bash
python gene_agent.py --refine reports/analysis_report_TIMESTAMP.yaml --verbose
```

### **3. Ask Questions**
```bash
python gene_agent.py --refine reports/analysis_report_TIMESTAMP.yaml --ask "What are the key hubs?"
```

### **4. Generate Biologist Summary**
```bash
python gene_agent.py --refine reports/analysis_report_TIMESTAMP.yaml --summarize "therapeutic targets"
```

## 📁 **File Structure**
```
gene_network_quality_agent/
├── gene_agent.py              # Main CLI
├── agent/tools/               # Analysis tools
├── models/                    # Test BND networks
├── reports/                   # Generated reports
├── NEW_ARCHITECTURE.md        # Architecture documentation
└── SETUP.md                   # This file
```

## 🔧 **Configuration**

### **Environment Variables**
- `OPENAI_API_KEY`: Your OpenAI API key (optional - uses mock if not set)

### **Command Line Options**
- `--model`: AI model to use (default: gpt-3.5-turbo)
- `--verbose`: Enable detailed logging
- `--help`: Show usage information

## 🎯 **Usage Examples**

### **Complete Workflow**
```bash
# 1. Initial analysis
python gene_agent.py models/simple_good_network.bnd --default-pipeline

# 2. LLM refinement
python gene_agent.py --refine reports/analysis_report_20251014_165255.yaml

# 3. Specific questions
python gene_agent.py --refine reports/analysis_report_20251014_165255.yaml \
  --ask "What therapeutic targets does this network suggest?"

# 4. Research summary
python gene_agent.py --refine reports/analysis_report_20251014_165255.yaml \
  --summarize "cancer research" --model gpt-3.5-turbo
```

### **Different Research Focuses**
```bash
# Drug discovery
python gene_agent.py --refine report.yaml --summarize "drug discovery"

# Systems biology
python gene_agent.py --refine report.yaml --summarize "systems biology"

# Clinical applications
python gene_agent.py --refine report.yaml --summarize "clinical applications"
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **OpenAI API Quota Exceeded**
```
Error: You exceeded your current quota
```
**Solution**: System automatically falls back to mock responses

#### **Missing Dependencies**
```
ImportError: No module named 'openai'
```
**Solution**: `pip install openai networkx pyyaml`

#### **No Network File**
```
Error: Network file required for --default-pipeline
```
**Solution**: Provide a .bnd file: `python gene_agent.py network.bnd --default-pipeline`

### **Debug Mode**
```bash
# Enable verbose logging for debugging
python gene_agent.py models/simple_good_network.bnd --default-pipeline --verbose
```

## 📊 **Output Files**

### **Technical Reports** (YAML)
- `reports/analysis_report_TIMESTAMP.yaml` - LLM-friendly structured report
- `reports/analysis_report_full_TIMESTAMP.yaml` - Complete report with raw data

### **Biologist Summaries** (Markdown)
- `reports/analysis_report_TIMESTAMP_biologist_summary_FOCUS.md`

## 🔄 **Mock Response Mode**

When OpenAI API is unavailable, the system provides realistic mock responses:

### **Features**
- ✅ **Refine Mode**: Suggests deep topology analysis and pathway validation
- ✅ **Ask Mode**: Provides detailed answers about network hubs and mechanisms  
- ✅ **Summarize Mode**: Generates comprehensive therapeutic target analysis
- ✅ **Full Workflow**: Complete demonstration without API dependency

### **Benefits**
- 🎭 **Demo-Ready**: Show functionality without API costs
- 🔄 **Fallback**: Graceful degradation when API fails
- 📚 **Educational**: Learn system capabilities offline
- 🧪 **Testing**: Validate workflows without external dependencies

## 🚀 **Production Deployment**

### **Security Best Practices**
1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Implement rate limiting** for API calls
4. **Add input validation** for user queries
5. **Enable audit logging** for production use

### **Scaling Considerations**
1. **Cache LLM responses** to reduce API costs
2. **Implement request queuing** for high volume
3. **Add database storage** for report persistence
4. **Monitor API usage** and costs
5. **Implement user authentication** for multi-user environments

## 📞 **Support**

### **Documentation**
- `NEW_ARCHITECTURE.md` - Complete architecture overview
- `--help` - CLI usage and examples
- Code comments - Inline documentation

### **Testing**
```bash
# Test all modes with mock responses
python gene_agent.py models/simple_good_network.bnd --default-pipeline
python gene_agent.py --refine reports/latest_report.yaml
python gene_agent.py --refine reports/latest_report.yaml --ask "Test question"
python gene_agent.py --refine reports/latest_report.yaml --summarize "test focus"
```

**The Gene Agent is ready for production use with proper API key configuration!** 🧬✨
