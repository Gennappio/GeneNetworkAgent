#!/usr/bin/env python3
"""
Gene Network Quality Agent - Redesigned CLI Architecture

A structured approach to gene network analysis with LLM integration.
"""

import argparse
import sys
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeneAgent:
    """Main Gene Network Quality Agent with structured CLI interface"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)
            
        # OpenAI API key from environment variable
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            logger.warning("⚠️  OPENAI_API_KEY not set. Using mock responses for demonstration.")
            self.use_mock_responses = True
        else:
            self.use_mock_responses = False
        
        # Set up OpenAI
        if not self.use_mock_responses:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                logger.info("✅ OpenAI client initialized")
            except ImportError:
                logger.error("❌ OpenAI package not installed. Run: pip install openai")
                logger.info("🔄 Falling back to mock responses")
                self.use_mock_responses = True
        else:
            logger.info("🎭 Using mock LLM responses for demonstration")
            
    def run_default_pipeline(self, model_path: str) -> str:
        """
        Run hardcoded analysis pipeline and generate programmer/LLM readable report
        
        Args:
            model_path: Path to .bnd network file
            
        Returns:
            Path to generated report file
        """
        logger.info(f"🔄 Running default pipeline on {model_path}")
        
        # Import our existing tools
        from agent.tools.load_bnd_network import execute as load_network
        from agent.tools.analyze_topology import execute as analyze_topology
        from agent.tools.analyze_dynamics import execute as analyze_dynamics
        from agent.tools.test_perturbations import execute as test_perturbations
        from agent.tools.validate_biology import execute as validate_biology
        
        # Initialize state
        state = {"model_path": model_path}
        
        # Step 1: Load network
        logger.info("📝 Step 1: Loading BND network...")
        result = load_network(state)
        state.update(result)
        
        # Step 2: Analyze topology
        logger.info("🔍 Step 2: Analyzing network topology...")
        result = analyze_topology(state)
        state.update(result)
        
        # Step 3: Analyze dynamics
        logger.info("⚡ Step 3: Analyzing network dynamics...")
        result = analyze_dynamics(state)
        state.update(result)
        
        # Step 4: Test perturbations
        logger.info("🧪 Step 4: Testing perturbations...")
        result = test_perturbations(state)
        state.update(result)
        
        # Step 5: Validate biology
        logger.info("🧬 Step 5: Validating biological plausibility...")
        result = validate_biology(state)
        state.update(result)
        
        # Step 6: Generate structured report
        logger.info("📊 Step 6: Generating structured report...")
        report_path = self._generate_structured_report(state)
        
        logger.info(f"✅ Default pipeline completed. Report: {report_path}")
        return report_path
        
    def refine_analysis(self, report_path: str, ask_query: Optional[str] = None, model: str = "gpt-3.5-turbo") -> str:
        """
        Use LLM to review report and create additional analysis pipeline
        
        Args:
            report_path: Path to existing report
            ask_query: Optional specific question to ask
            model: AI model to use
            
        Returns:
            Path to updated report
        """
        logger.info(f"🤖 Refining analysis using {model}")
        
        # Load existing report
        with open(report_path, 'r') as f:
            report_data = yaml.safe_load(f)
            
        # Create LLM prompt
        if ask_query:
            prompt = self._create_ask_prompt(report_data, ask_query)
        else:
            prompt = self._create_refine_prompt(report_data)
            
        # Get LLM response
        llm_response = self._call_llm(prompt, model)
        
        # Parse LLM response and execute additional analysis
        additional_analysis = self._parse_llm_response(llm_response)
        
        # Execute additional tools if needed
        updated_report_path = self._execute_additional_analysis(report_path, additional_analysis)
        
        logger.info(f"✅ Refinement completed. Updated report: {updated_report_path}")
        return updated_report_path
        
    def summarize_for_biologist(self, report_path: str, summary_focus: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Generate biologist-friendly summary from technical report
        
        Args:
            report_path: Path to technical report
            summary_focus: Focus area for summary
            model: AI model to use
            
        Returns:
            Path to biologist summary
        """
        logger.info(f"📝 Creating biologist summary with focus: {summary_focus}")
        
        # Load technical report
        with open(report_path, 'r') as f:
            report_data = yaml.safe_load(f)
            
        # Create summarization prompt
        prompt = self._create_summary_prompt(report_data, summary_focus)
        
        # Get LLM summary
        summary = self._call_llm(prompt, model)
        
        # Save biologist-friendly summary
        summary_path = self._save_biologist_summary(report_path, summary, summary_focus)
        
        logger.info(f"✅ Biologist summary created: {summary_path}")
        return summary_path
        
    def _generate_structured_report(self, state: Dict[str, Any]) -> str:
        """Generate structured report readable by programmers and LLMs"""
        
        # Create reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Generate timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create structured report
        report = {
            "metadata": {
                "timestamp": timestamp,
                "network_file": state.get("model_path"),
                "network_name": state.get("network_name", "Unknown"),
                "analysis_type": "default_pipeline",
                "version": "2.0"
            },
            "network_properties": {
                "total_nodes": len(state.get("model_data", {}).get("nodes", [])),
                "input_nodes": state.get("model_data", {}).get("input_nodes", 0),
                "logic_nodes": len(state.get("model_data", {}).get("nodes", [])) - state.get("model_data", {}).get("input_nodes", 0)
            },
            "topology_analysis": state.get("topology_results", {}),
            "dynamics_analysis": state.get("dynamics_results", {}),
            "perturbation_analysis": state.get("perturbation_results", {}),
            "biological_validation": state.get("validation_results", {}),
            "quality_metrics": {
                "biological_plausibility": state.get("validation_results", {}).get("plausibility", 0),
                "issues_found": len(state.get("validation_results", {}).get("issues", [])),
                "overall_quality": self._calculate_overall_quality(state)
            },
            "recommendations": state.get("validation_results", {}).get("recommendations", []),
            "raw_data": {
                "full_state": state  # For LLM access to complete data
            }
        }
        
        # Save report (exclude raw_data for LLM consumption)
        report_path = reports_dir / f"analysis_report_{timestamp}.yaml"
        
        # Create LLM-friendly version without raw_data
        llm_report = {k: v for k, v in report.items() if k != "raw_data"}
        
        with open(report_path, 'w') as f:
            yaml.dump(llm_report, f, default_flow_style=False, indent=2)
            
        # Save full report with raw data separately
        full_report_path = reports_dir / f"analysis_report_full_{timestamp}.yaml"
        with open(full_report_path, 'w') as f:
            yaml.dump(report, f, default_flow_style=False, indent=2)
            
        logger.info(f"📄 LLM-friendly report: {report_path}")
        logger.info(f"📄 Full report with raw data: {full_report_path}")
        
        return str(report_path)
        
    def _calculate_overall_quality(self, state: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        plausibility = state.get("validation_results", {}).get("plausibility", 0)
        issues = len(state.get("validation_results", {}).get("issues", []))
        
        # Simple quality calculation
        quality = plausibility * (1 - min(issues * 0.1, 0.5))
        return round(quality, 2)
        
    def _call_llm(self, prompt: str, model: str) -> str:
        """Call OpenAI LLM with prompt"""
        if self.use_mock_responses:
            logger.info("🎭 Using mock LLM response")
            return self._get_mock_llm_response(prompt)
            
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert in gene network analysis and bioinformatics."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ LLM call failed: {e}")
            logger.info("🔄 Falling back to mock response")
            return self._get_mock_llm_response(prompt)
            
    def _get_mock_llm_response(self, prompt: str) -> str:
        """Generate mock LLM response for demonstration when API is unavailable"""
        if "biologist" in prompt.lower() or "summary" in prompt.lower() or "therapeutic" in prompt.lower() or "cancer" in prompt.lower():
            return '''
# Gene Network Analysis: Therapeutic Target Identification

## Executive Summary
This p53 pathway network analysis reveals several potential therapeutic intervention points for cancer treatment. The network demonstrates key regulatory mechanisms involved in DNA damage response and cell fate determination.

## Key Therapeutic Targets

### Primary Targets
1. **p53 (TP53)** - Central tumor suppressor
   - **Therapeutic Strategy**: Restore p53 function in cancers with wild-type p53
   - **Drug Classes**: MDM2 inhibitors (e.g., Nutlin-3), p53 activators
   - **Clinical Relevance**: Mutated in ~50% of cancers

2. **MDM2** - p53 negative regulator
   - **Therapeutic Strategy**: Inhibit MDM2-p53 interaction
   - **Drug Classes**: Small molecule inhibitors, stapled peptides
   - **Clinical Status**: Several compounds in clinical trials

### Secondary Targets
3. **BCL2** - Anti-apoptotic protein
   - **Therapeutic Strategy**: Promote apoptosis in cancer cells
   - **Drug Classes**: BCL2 inhibitors (e.g., Venetoclax)
   - **Clinical Applications**: Approved for certain blood cancers

4. **p21 (CDKN1A)** - Cell cycle inhibitor
   - **Therapeutic Strategy**: Modulate cell cycle progression
   - **Approach**: Combination therapies with CDK inhibitors

## Network Vulnerabilities
- **Disconnected components**: Suggest missing regulatory links that could be targeted
- **Oscillatory behavior**: Indicates potential for destabilizing cancer cell dynamics
- **Growth factor dependency**: Opportunity for growth factor receptor inhibition

## Clinical Implications
1. **Combination Therapy**: Target multiple nodes simultaneously
2. **Biomarker Development**: Use network state as treatment response predictor
3. **Resistance Mechanisms**: Monitor pathway rewiring during treatment

## Recommendations for Drug Development
1. Focus on p53-MDM2 axis for solid tumors
2. Develop BCL2 family modulators for hematologic malignancies
3. Consider network-based combination strategies
4. Validate targets in patient-derived models
'''
        elif "refine" in prompt.lower() or "recommend" in prompt.lower():
            return '''
{
    "recommended_tools": ["deep_topology_analysis", "pathway_validator"],
    "reasoning": "The network shows disconnected components and unstable dynamics. Deep topology analysis would help identify structural issues, and pathway validation would assess biological coherence of the p53 pathway.",
    "priority": "high"
}
'''
        elif "question" in prompt.lower() or "ask" in prompt.lower():
            return '''
{
    "answer": "Based on the analysis, p53 appears to be a central regulatory hub in this network. It receives input from DNA_damage and influences multiple downstream pathways including apoptosis (via BCL2 inhibition) and cell cycle arrest (via p21 activation). The network shows some instability which may indicate missing regulatory mechanisms.",
    "recommended_tools": ["pathway_validator", "deep_topology_analysis"],
    "confidence": "high"
}
'''
        else:
            return '''
This gene network represents a simplified p53 pathway with key components for DNA damage response. The network includes:

**Key Findings:**
- p53 acts as a central tumor suppressor responding to DNA damage
- Two main output pathways: apoptosis and growth arrest
- BCL2 provides anti-apoptotic regulation
- Growth factors promote proliferation when conditions are favorable

**Biological Significance:**
- The p53 pathway is crucial for preventing cancer by eliminating damaged cells
- The balance between apoptosis and growth arrest determines cell fate
- Dysregulation of this pathway is implicated in many cancers

**Recommendations:**
- Consider adding p53 degradation mechanisms (e.g., MDM2 feedback)
- Include additional DNA repair pathways
- Add cell cycle checkpoints for more realistic dynamics
'''

    def _create_refine_prompt(self, report_data: Dict[str, Any]) -> str:
        """Create prompt for LLM to review and refine analysis"""
        return f"""
Please review this gene network analysis report and suggest additional analyses that would be valuable:

NETWORK: {report_data.get('metadata', {}).get('network_name', 'Unknown')}
QUALITY SCORE: {report_data.get('quality_metrics', {}).get('overall_quality', 0)}
ISSUES FOUND: {report_data.get('quality_metrics', {}).get('issues_found', 0)}

CURRENT ANALYSIS:
- Topology: {json.dumps(report_data.get('topology_analysis', {}), indent=2)}
- Dynamics: {json.dumps(report_data.get('dynamics_analysis', {}), indent=2)}
- Biology: {json.dumps(report_data.get('biological_validation', {}), indent=2)}

Based on this analysis, what additional tools or analyses would you recommend?
Available tools: deep_topology_analysis, pathway_validator

Respond with JSON format:
{{
    "recommended_tools": ["tool1", "tool2"],
    "reasoning": "Why these tools would be helpful",
    "priority": "high/medium/low"
}}
"""

    def _create_ask_prompt(self, report_data: Dict[str, Any], query: str) -> str:
        """Create prompt for specific user question"""
        return f"""
Based on this gene network analysis report, please answer the following question:

QUESTION: {query}

NETWORK DATA:
{json.dumps(report_data, indent=2)}

Please provide a detailed answer and suggest any additional analyses that would help answer this question better.

Respond with JSON format:
{{
    "answer": "Your detailed answer",
    "recommended_tools": ["tool1", "tool2"],
    "confidence": "high/medium/low"
}}
"""

    def _create_summary_prompt(self, report_data: Dict[str, Any], focus: str) -> str:
        """Create prompt for biologist summary"""
        return f"""
Please create a biologist-friendly summary of this gene network analysis with focus on: {focus}

TECHNICAL REPORT:
{json.dumps(report_data, indent=2)}

Create a summary that:
1. Uses biological terminology appropriate for researchers
2. Explains the significance of findings
3. Provides actionable insights
4. Focuses on: {focus}

Format as a clear, structured report suitable for publication or presentation.
"""

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "Could not parse LLM response"}
        except Exception as e:
            logger.error(f"❌ Failed to parse LLM response: {e}")
            return {"error": str(e)}

    def _execute_additional_analysis(self, report_path: str, analysis_plan: Dict[str, Any]) -> str:
        """Execute additional analysis based on LLM recommendations"""
        # This would integrate with our tool system
        # For now, just log the recommendations
        logger.info(f"📋 LLM Recommendations: {analysis_plan}")

        # Return original report path for now
        # TODO: Implement actual additional tool execution
        return report_path

    def _save_biologist_summary(self, report_path: str, summary: str, focus: str) -> str:
        """Save biologist-friendly summary"""
        summary_path = report_path.replace('.yaml', f'_biologist_summary_{focus.replace(" ", "_")}.md')

        with open(summary_path, 'w') as f:
            f.write(f"# Gene Network Analysis Summary\n\n")
            f.write(f"**Focus:** {focus}\n\n")
            f.write(f"**Source Report:** {report_path}\n\n")
            f.write(summary)

        return summary_path


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Gene Network Quality Agent - Structured Analysis with LLM Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run default analysis pipeline
  python gene_agent.py network.bnd --default-pipeline

  # Refine analysis with LLM review
  python gene_agent.py --refine report.yaml

  # Ask specific question about analysis
  python gene_agent.py --refine report.yaml --ask "What are the key regulatory hubs?"

  # Create biologist summary
  python gene_agent.py --refine report.yaml --summarize "therapeutic targets"
        """
    )

    # Positional argument for network file (optional)
    parser.add_argument('network_file', nargs='?', help='Path to .bnd network file')

    # Mode flags
    parser.add_argument('--default-pipeline', action='store_true',
                       help='Run hardcoded analysis pipeline and generate structured report')
    parser.add_argument('--refine', metavar='REPORT_FILE',
                       help='Refine analysis using LLM review of existing report')
    parser.add_argument('--ask', metavar='QUESTION',
                       help='Ask specific question about the analysis (use with --refine)')
    parser.add_argument('--summarize', metavar='FOCUS',
                       help='Create biologist-friendly summary with given focus (use with --refine)')

    # Options
    parser.add_argument('--model', default='gpt-3.5-turbo',
                       help='AI model to use (default: gpt-3.5-turbo)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')

    args = parser.parse_args()

    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # Initialize agent
    agent = GeneAgent(verbose=args.verbose)

    try:
        if args.default_pipeline:
            if not args.network_file:
                print("❌ Error: Network file required for --default-pipeline")
                sys.exit(1)
            report_path = agent.run_default_pipeline(args.network_file)
            print(f"✅ Analysis complete. Report: {report_path}")

        elif args.refine:
            if args.ask:
                report_path = agent.refine_analysis(args.refine, ask_query=args.ask, model=args.model)
                print(f"✅ Question answered. Updated report: {report_path}")
            elif args.summarize:
                summary_path = agent.summarize_for_biologist(args.refine, args.summarize, model=args.model)
                print(f"✅ Summary created: {summary_path}")
            else:
                report_path = agent.refine_analysis(args.refine, model=args.model)
                print(f"✅ Analysis refined. Updated report: {report_path}")

        else:
            print("❌ Error: Please specify a mode (--default-pipeline or --refine)")
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
