#!/usr/bin/env python3
"""
Gene Network Quality Agent - LangChain Production Version

A structured approach to gene network analysis with LLM integration using LangChain.
"""

import argparse
import sys
import os
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
            logger.error("OPENAI_API_KEY environment variable not set")
            sys.exit(1)

        # Set up LangChain ChatOpenAI
        try:
            self.llm = ChatOpenAI(
                api_key=self.openai_api_key,
                model="gpt-3.5-turbo",
                temperature=0.1,
                max_tokens=2000
            )
            logger.info("LangChain ChatOpenAI initialized")
        except ImportError:
            logger.error("LangChain packages not installed. Run: pip install langchain langchain-openai")
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
        Run analysis pipeline with natural language communication between agents

        Args:
            model_path: Path to .bnd network file

        Returns:
            Path to generated report file
        """
        logger.info(f"Running analysis pipeline on {model_path}")

        # Define the analysis agents in order
        agents = [
            ("Network Loader", "agent.tools.load_bnd_network"),
            ("Topology Analyzer", "agent.tools.analyze_topology"),
            ("Dynamics Analyzer", "agent.tools.analyze_dynamics"),
            ("Perturbation Tester", "agent.tools.test_perturbations"),
            ("Biology Validator", "agent.tools.validate_biology")
        ]

        # Initialize with just the model path
        context = f"Analyzing gene network: {model_path}"
        analysis_results = []

        # Run each agent and collect natural language results
        for step, (agent_name, agent_module) in enumerate(agents, 1):
            logger.info(f"Step {step}: {agent_name}...")

            # Import and execute agent
            module_parts = agent_module.split('.')
            module = __import__(agent_module, fromlist=[module_parts[-1]])
            agent_result = module.execute_natural_language(context, model_path)

            # Collect the natural language evaluation
            analysis_results.append(f"## {agent_name}\n{agent_result}\n")

            # Update context for next agent
            context += f"\n\nPrevious analysis from {agent_name}:\n{agent_result}"

        # Generate final report
        logger.info("Generating final report...")
        report_path = self._generate_natural_language_report(model_path, analysis_results)

        logger.info(f"Analysis pipeline completed. Report: {report_path}")
        return report_path
        
    def refine_analysis(self, report_path: str, ask_query: Optional[str] = None, model: str = "gpt-3.5-turbo") -> str:
        """
        Use LangChain to review natural language report and provide insights

        Args:
            report_path: Path to existing natural language report
            ask_query: Optional specific question to ask about the report
            model: AI model to use (ignored, using LangChain configuration)

        Returns:
            Natural language response with insights or answer to question
        """
        logger.info("Refining analysis with LangChain LLM review...")

        # Load existing report (natural language)
        with open(report_path, 'r') as f:
            report_content = f.read()

        # Extract model path from report path for potential tool execution
        model_path = self._extract_model_path_from_report(report_path)

        # Track token usage
        with get_openai_callback() as cb:
            if ask_query:
                # Handle question answering about the report
                result, recommended_tools = self._answer_question_about_report(report_content, ask_query)
                logger.info(f"Token usage: {cb.total_tokens} tokens, ${cb.total_cost:.4f}")
                logger.info(f"Question answered: {result[:100]}...")

                # Execute recommended tools if any
                if recommended_tools and model_path:
                    logger.info(f"Executing recommended tools: {recommended_tools}")
                    additional_analysis = self._execute_recommended_tools(model_path, recommended_tools)
                    if additional_analysis:
                        result += f"\n\n## Additional Analysis Results\n{additional_analysis}"

                return result
            else:
                # Handle analysis refinement suggestions
                result, recommended_tools = self._get_refinement_suggestions(report_content)
                logger.info(f"Token usage: {cb.total_tokens} tokens, ${cb.total_cost:.4f}")
                logger.info(f"Refinement suggestions provided")

                # Execute recommended tools if any
                if recommended_tools and model_path:
                    logger.info(f"Executing recommended tools: {recommended_tools}")
                    additional_analysis = self._execute_recommended_tools(model_path, recommended_tools)
                    if additional_analysis:
                        result += f"\n\n## Additional Analysis Results\n{additional_analysis}"

                return result
        
    def summarize_for_biologist(self, report_path: str, summary_focus: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Generate biologist-friendly summary from natural language report

        Args:
            report_path: Path to natural language report
            summary_focus: Focus area for summary
            model: AI model to use (ignored, using LangChain configuration)

        Returns:
            Path to biologist summary
        """
        logger.info(f"Creating biologist summary with focus: {summary_focus}")

        # Load natural language report
        with open(report_path, 'r') as f:
            report_content = f.read()

        # Track token usage and generate summary
        with get_openai_callback() as cb:
            result = self._generate_focused_summary(report_content, summary_focus)
            logger.info(f"Token usage: {cb.total_tokens} tokens, ${cb.total_cost:.4f}")

        # Save biologist-friendly summary
        summary_path = self._save_biologist_summary(report_path, result, summary_focus)

        logger.info(f"Biologist summary created: {summary_path}")
        return summary_path
        
    def _generate_natural_language_report(self, model_path: str, analysis_results: List[str]) -> str:
        """Generate natural language report from agent evaluations"""

        # Create reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        # Generate timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create natural language report
        report_content = f"""# Gene Network Analysis Report

            **Network:** {Path(model_path).name}
            **Analysis Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            **Report Type:** Comprehensive Analysis Pipeline

            ## Executive Summary

            This report presents a comprehensive analysis of the gene network using multiple specialized agents. Each agent provides an independent evaluation in natural language, making the results accessible to both technical and biological researchers.

            ## Detailed Analysis Results

            {''.join(analysis_results)}

            ## Conclusion

            The analysis pipeline has completed successfully. Each agent has provided its specialized evaluation above. This natural language format allows for easy interpretation and integration of results across different analytical perspectives.

            ---
            *Generated by Gene Network Quality Agent - Natural Language Pipeline*
            """

        # Save natural language report
        report_path = reports_dir / f"analysis_report_{timestamp}.md"
        with open(report_path, 'w') as f:
            f.write(report_content)

        logger.info(f"Natural language report: {report_path}")

        return str(report_path)

    def _get_refinement_suggestions(self, report_content: str) -> tuple[str, list]:
        """Get LLM suggestions for improving the analysis using natural language"""

        available_tools = [
            "Network Loader - loads and validates BND network files",
            "Topology Analyzer - analyzes network structure, connectivity, cycles",
            "Dynamics Analyzer - simulates network dynamics and attractors",
            "Perturbation Tester - tests knockout and overexpression effects",
            "Biology Validator - validates biological plausibility"
        ]

        # Create a simple prompt for refinement suggestions
        prompt = f"""You are an expert in gene network analysis. Please review this analysis report and provide suggestions for improvement or additional insights.

Available analysis tools:
{chr(10).join([f"- {tool}" for tool in available_tools])}

            Report to review:
            {report_content}

            Please provide:
            1. Key strengths of the current analysis
            2. Areas that could be improved or expanded
            3. Specific suggestions for additional analysis
            4. Any potential concerns or limitations
            5. If additional tool execution would be helpful, specify which tools should be run and why

            Respond in clear, natural language suitable for researchers."""

        try:
            # Use simple chain without complex parsing
            chain = self.llm
            result = chain.invoke([{"role": "user", "content": prompt}])

            # Parse response to extract tool recommendations
            response_text = result.content
            recommended_tools = self._extract_tool_recommendations(response_text)

            return response_text, recommended_tools
        except Exception as e:
            logger.error(f"Refinement suggestions failed: {e}")
            return f"Error generating refinement suggestions: {e}", []

    def _answer_question_about_report(self, report_content: str, question: str) -> tuple[str, list]:
        """Answer specific question about the natural language report"""

        available_tools = [
            "Network Loader - loads and validates BND network files",
            "Topology Analyzer - analyzes network structure, connectivity, cycles",
            "Dynamics Analyzer - simulates network dynamics and attractors",
            "Perturbation Tester - tests knockout and overexpression effects",
            "Biology Validator - validates biological plausibility"
        ]

        prompt = f"""You are an expert in gene network analysis. Please answer the following question based on the analysis report provided.

Available analysis tools:
{chr(10).join([f"- {tool}" for tool in available_tools])}

            Question: {question}

            Analysis Report:
            {report_content}

            Please provide a detailed, accurate answer based on the information in the report. If the report doesn't contain enough information to answer the question, please state that clearly and suggest what additional analysis might be needed.

            If running specific analysis tools would help answer the question better, mention which tools should be executed and why.

            Respond in clear, natural language suitable for researchers."""

        try:
            # Use simple chain without complex parsing
            chain = self.llm
            result = chain.invoke([{"role": "user", "content": prompt}])

            # Parse response to extract tool recommendations
            response_text = result.content
            recommended_tools = self._extract_tool_recommendations(response_text)

            return response_text, recommended_tools
        except Exception as e:
            logger.error(f"Question answering failed: {e}")
            return f"Error processing question: {e}", []

    def _extract_tool_recommendations(self, response_text: str) -> list:
        """Extract tool recommendations from LLM response"""
        recommended_tools = []

        # Simple keyword-based extraction
        tool_keywords = {
            "Network Loader": ["network loader", "load network", "loading", "bnd file"],
            "Topology Analyzer": ["topology", "structure", "connectivity", "cycles", "feedback"],
            "Dynamics Analyzer": ["dynamics", "simulation", "attractors", "stability", "temporal"],
            "Perturbation Tester": ["perturbation", "knockout", "overexpression", "robustness"],
            "Biology Validator": ["biological", "validation", "plausibility", "biology"]
        }

        response_lower = response_text.lower()

        for tool_name, keywords in tool_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                if "should be run" in response_lower or "recommend" in response_lower or "suggest" in response_lower:
                    recommended_tools.append(tool_name)

        return recommended_tools

    def _execute_recommended_tools(self, model_path: str, recommended_tools: list) -> str:
        """Execute recommended tools and return results"""
        if not recommended_tools:
            return ""

        logger.info(f"Executing recommended tools: {', '.join(recommended_tools)}")

        # Map tool names to modules
        tool_modules = {
            "Network Loader": "agent.tools.load_bnd_network",
            "Topology Analyzer": "agent.tools.analyze_topology",
            "Dynamics Analyzer": "agent.tools.analyze_dynamics",
            "Perturbation Tester": "agent.tools.test_perturbations",
            "Biology Validator": "agent.tools.validate_biology"
        }

        results = []
        context = f"Analyzing gene network: {model_path}"

        for tool_name in recommended_tools:
            if tool_name in tool_modules:
                try:
                    module_name = tool_modules[tool_name]
                    module_parts = module_name.split('.')
                    module = __import__(module_name, fromlist=[module_parts[-1]])
                    result = module.execute_natural_language(context, model_path)
                    results.append(f"## {tool_name}\n{result}\n")
                    context += f"\n\nPrevious analysis from {tool_name}:\n{result}"
                except Exception as e:
                    logger.error(f"Failed to execute {tool_name}: {e}")
                    results.append(f"## {tool_name}\nFailed to execute: {e}\n")

        return "\n".join(results)

    def _extract_model_path_from_report(self, report_path: str) -> str:
        """Extract the original model path from the report file"""
        try:
            with open(report_path, 'r') as f:
                content = f.read()

            # Look for the network name in the report
            import re
            match = re.search(r'\*\*Network:\*\* (.+?)\.bnd', content)
            if match:
                network_name = match.group(1)
                # Try to find the corresponding .bnd file
                possible_paths = [
                    f"models/{network_name}.bnd",
                    f"{network_name}.bnd",
                    f"../models/{network_name}.bnd"
                ]

                for path in possible_paths:
                    if os.path.exists(path):
                        return path

            return None
        except Exception as e:
            logger.error(f"Failed to extract model path from report: {e}")
            return None

    def _generate_focused_summary(self, report_content: str, focus: str) -> str:
        """Generate focused biologist-friendly summary from natural language report"""

        prompt = f"""You are an expert biologist and researcher. Please create a focused summary of this gene network analysis report with emphasis on: {focus}

            Original Analysis Report:
            {report_content}

            Please create a comprehensive summary that:
            1. Highlights findings most relevant to {focus}
            2. Explains the biological significance in accessible language
            3. Identifies key genes, pathways, and mechanisms
            4. Discusses potential therapeutic implications if relevant
            5. Suggests future research directions

            Format your response as a well-structured markdown document suitable for publication or presentation to biological researchers."""

        try:
            # Use simple chain without complex parsing
            chain = self.llm
            result = chain.invoke([{"role": "user", "content": prompt}])
            return result.content
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return f"Error generating summary: {e}"



    def _execute_additional_analysis(self, report_path: str, analysis_plan: Dict[str, Any]) -> str:
        """Execute additional analysis based on LLM recommendations"""
        logger.info(f"LLM Recommendations: {analysis_plan}")

        # Log recommendations for future implementation
        # Additional tool execution can be implemented here as needed
        return report_path

    def _save_biologist_summary(self, report_path: str, summary: str, focus: str) -> str:
        """Save biologist-friendly summary"""
        summary_path = report_path.replace('.md', f'_biologist_summary_{focus.replace(" ", "_")}.md')

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
                print("Error: Network file required for --default-pipeline")
                sys.exit(1)
            report_path = agent.run_default_pipeline(args.network_file)
            print(f"Analysis complete. Report: {report_path}")

        elif args.refine:
            if args.ask:
                answer = agent.refine_analysis(args.refine, ask_query=args.ask, model=args.model)
                print(answer)
            elif args.summarize:
                summary_path = agent.summarize_for_biologist(args.refine, args.summarize, model=args.model)
                print(f"Summary created: {summary_path}")
            else:
                report_path = agent.refine_analysis(args.refine, model=args.model)
                print(f"Analysis refined. Updated report: {report_path}")

        else:
            print("Error: Please specify a mode (--default-pipeline or --refine)")
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
