#!/usr/bin/env python3
"""
Gene Network Quality Agent - LangChain Production Version

A structured approach to gene network analysis with LLM integration using LangChain.
"""

import argparse
import sys
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.callbacks import get_openai_callback
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic models for structured outputs
class AnalysisRecommendation(BaseModel):
    """Model for LLM analysis recommendations"""
    recommended_tools: List[str] = Field(description="List of recommended analysis tools")
    reasoning: str = Field(description="Explanation of why these tools are recommended")
    priority: str = Field(description="Priority level: high, medium, or low")

class QuestionAnswer(BaseModel):
    """Model for LLM question responses"""
    answer: str = Field(description="Detailed answer to the user's question")
    confidence: str = Field(description="Confidence level: high, medium, or low")
    recommended_tools: List[str] = Field(description="Additional tools that might help", default=[])

class BiologistSummary(BaseModel):
    """Model for biologist-friendly summaries"""
    summary: str = Field(description="Comprehensive summary in markdown format")
    key_findings: List[str] = Field(description="List of key findings")
    therapeutic_targets: List[str] = Field(description="Potential therapeutic targets", default=[])
    recommendations: List[str] = Field(description="Research recommendations", default=[])

class GeneAgent:
    """Main Gene Network Quality Agent with LangChain integration"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)

        # OpenAI API key from environment variable
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            logger.error("❌ OPENAI_API_KEY environment variable not set")
            sys.exit(1)

        # Set up LangChain ChatOpenAI
        try:
            self.llm = ChatOpenAI(
                api_key=self.openai_api_key,
                model="gpt-3.5-turbo",
                temperature=0.1,
                max_tokens=2000
            )
            logger.info("✅ LangChain ChatOpenAI initialized")
        except ImportError:
            logger.error("❌ LangChain packages not installed. Run: pip install langchain langchain-openai")
            sys.exit(1)

        # Set up output parsers
        self.analysis_parser = JsonOutputParser(pydantic_object=AnalysisRecommendation)
        self.question_parser = JsonOutputParser(pydantic_object=QuestionAnswer)
        self.summary_parser = JsonOutputParser(pydantic_object=BiologistSummary)

        # Create prompt templates
        self._setup_prompt_templates()

    def _setup_prompt_templates(self):
        """Set up LangChain prompt templates"""
        # Analysis refinement prompt
        self.refine_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert in gene network analysis and bioinformatics. Provide structured recommendations for additional analysis."),
            ("user", """Please review this gene network analysis report and suggest additional analyses:

NETWORK: {network_name}
QUALITY SCORE: {quality_score}
ISSUES FOUND: {issues_found}

CURRENT ANALYSIS:
- Topology: {topology_analysis}
- Dynamics: {dynamics_analysis}
- Biology: {biological_validation}

Based on this analysis, what additional tools or analyses would you recommend?
Available tools: deep_topology_analysis, pathway_validator

{format_instructions}""")
        ])

        # Question answering prompt
        self.question_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert in gene network analysis and bioinformatics. Answer questions based on the provided analysis data."),
            ("user", """Based on this gene network analysis report, please answer the following question:

QUESTION: {question}

NETWORK DATA:
- Network: {network_name}
- Quality Score: {quality_score}
- Topology: {topology_analysis}
- Dynamics: {dynamics_analysis}
- Biology: {biological_validation}

{format_instructions}""")
        ])

        # Summary generation prompt
        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert biologist creating research summaries. Generate comprehensive, publication-ready summaries."),
            ("user", """Create a biologist-friendly summary of this gene network analysis with focus on: {focus}

NETWORK DATA:
- Network: {network_name}
- Quality Score: {quality_score}
- Nodes: {total_nodes}
- Topology: {topology_analysis}
- Dynamics: {dynamics_analysis}
- Biology: {biological_validation}

Create a comprehensive summary suitable for researchers in the field.

{format_instructions}""")
        ])

    def run_default_pipeline(self, model_path: str) -> str:
        """
        Run standard analysis pipeline and generate structured report

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
        Use LangChain to review report and create additional analysis pipeline

        Args:
            report_path: Path to existing report
            ask_query: Optional specific question to ask
            model: AI model to use (ignored, using LangChain configuration)

        Returns:
            Path to updated report or answer to question
        """
        logger.info("🔄 Refining analysis with LangChain LLM review...")

        # Load existing report
        with open(report_path, 'r') as f:
            report_data = yaml.safe_load(f)

        # Track token usage
        with get_openai_callback() as cb:
            if ask_query:
                # Handle question answering
                result = self._answer_question(report_data, ask_query)
                logger.info(f"💰 Token usage: {cb.total_tokens} tokens, ${cb.total_cost:.4f}")
                logger.info(f"✅ Question answered: {result.get('answer', 'No answer')[:100]}...")
                return result.get('answer', 'No answer provided')
            else:
                # Handle analysis refinement
                result = self._get_analysis_recommendations(report_data)
                logger.info(f"💰 Token usage: {cb.total_tokens} tokens, ${cb.total_cost:.4f}")

                # Execute additional tools if needed
                updated_report_path = self._execute_additional_analysis(report_path, result)

                logger.info(f"✅ Refinement completed. Updated report: {updated_report_path}")
                return updated_report_path
        
    def summarize_for_biologist(self, report_path: str, summary_focus: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Generate biologist-friendly summary using LangChain

        Args:
            report_path: Path to technical report
            summary_focus: Focus area for summary
            model: AI model to use (ignored, using LangChain configuration)

        Returns:
            Path to biologist summary
        """
        logger.info(f"📝 Creating biologist summary with focus: {summary_focus}")

        # Load technical report
        with open(report_path, 'r') as f:
            report_data = yaml.safe_load(f)

        # Track token usage and generate summary
        with get_openai_callback() as cb:
            result = self._generate_biologist_summary(report_data, summary_focus)
            logger.info(f"💰 Token usage: {cb.total_tokens} tokens, ${cb.total_cost:.4f}")

        # Save biologist-friendly summary
        summary_path = self._save_biologist_summary(report_path, result.get('summary', 'No summary generated'), summary_focus)

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

    def _get_analysis_recommendations(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get LLM recommendations for additional analysis using LangChain"""
        chain = self.refine_prompt | self.llm | self.analysis_parser

        return chain.invoke({
            "network_name": report_data.get('metadata', {}).get('network_name', 'Unknown'),
            "quality_score": report_data.get('quality_metrics', {}).get('overall_quality', 0),
            "issues_found": report_data.get('quality_metrics', {}).get('issues_found', 0),
            "topology_analysis": json.dumps(report_data.get('topology_analysis', {}), indent=2),
            "dynamics_analysis": json.dumps(report_data.get('dynamics_analysis', {}), indent=2),
            "biological_validation": json.dumps(report_data.get('biological_validation', {}), indent=2),
            "format_instructions": self.analysis_parser.get_format_instructions()
        })

    def _answer_question(self, report_data: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Answer specific question about analysis using LangChain"""
        try:
            # First try with parser
            chain = self.question_prompt | self.llm | self.question_parser

            result = chain.invoke({
                "question": question,
                "network_name": report_data.get('metadata', {}).get('network_name', 'Unknown'),
                "quality_score": report_data.get('quality_metrics', {}).get('overall_quality', 0),
                "topology_analysis": json.dumps(report_data.get('topology_analysis', {}), indent=2),
                "dynamics_analysis": json.dumps(report_data.get('dynamics_analysis', {}), indent=2),
                "biological_validation": json.dumps(report_data.get('biological_validation', {}), indent=2),
                "format_instructions": self.question_parser.get_format_instructions()
            })

            # Check if result is valid
            if isinstance(result, dict) and 'answer' in result:
                logger.debug(f"🔍 Question result: {result}")
                return result
            else:
                # Fallback: try without parser
                logger.warning("⚠️ Parser failed, trying without parser")
                chain_simple = self.question_prompt | self.llm
                raw_result = chain_simple.invoke({
                    "question": question,
                    "network_name": report_data.get('metadata', {}).get('network_name', 'Unknown'),
                    "quality_score": report_data.get('quality_metrics', {}).get('overall_quality', 0),
                    "topology_analysis": json.dumps(report_data.get('topology_analysis', {}), indent=2),
                    "dynamics_analysis": json.dumps(report_data.get('dynamics_analysis', {}), indent=2),
                    "biological_validation": json.dumps(report_data.get('biological_validation', {}), indent=2),
                    "format_instructions": self.question_parser.get_format_instructions()
                })

                # Try to extract JSON manually
                import re
                json_match = re.search(r'\{.*\}', raw_result.content, re.DOTALL)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group())
                        return parsed
                    except:
                        pass

                # Final fallback: return raw content
                logger.debug(f"🔍 Raw result content: {raw_result.content}")
                return {"answer": raw_result.content, "confidence": "medium", "recommended_tools": []}

        except Exception as e:
            logger.error(f"❌ Question answering failed: {e}")
            return {"answer": f"Error processing question: {e}", "confidence": "low", "recommended_tools": []}

    def _generate_biologist_summary(self, report_data: Dict[str, Any], focus: str) -> Dict[str, Any]:
        """Generate biologist-friendly summary using LangChain"""
        try:
            # Use simple chain without JSON parser for summary
            chain = self.summary_prompt | self.llm

            result = chain.invoke({
                "focus": focus,
                "network_name": report_data.get('metadata', {}).get('network_name', 'Unknown'),
                "quality_score": report_data.get('quality_metrics', {}).get('overall_quality', 0),
                "total_nodes": report_data.get('network_info', {}).get('total_nodes', 0),
                "topology_analysis": json.dumps(report_data.get('topology_analysis', {}), indent=2),
                "dynamics_analysis": json.dumps(report_data.get('dynamics_analysis', {}), indent=2),
                "biological_validation": json.dumps(report_data.get('biological_validation', {}), indent=2),
                "format_instructions": "Generate a comprehensive markdown summary suitable for biologists."
            })

            # Return the content directly as summary
            return {"summary": result.content, "key_findings": [], "therapeutic_targets": [], "recommendations": []}

        except Exception as e:
            logger.error(f"❌ Summary generation failed: {e}")
            return {"summary": f"Error generating summary: {e}", "key_findings": [], "therapeutic_targets": [], "recommendations": []}



    def _execute_additional_analysis(self, report_path: str, analysis_plan: Dict[str, Any]) -> str:
        """Execute additional analysis based on LLM recommendations"""
        logger.info(f"📋 LLM Recommendations: {analysis_plan}")

        # Log recommendations for future implementation
        # Additional tool execution can be implemented here as needed
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
                       help='Run standard analysis pipeline and generate structured report')
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
