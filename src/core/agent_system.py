"""
Legal Intelligence Agent System - Core Agent Implementation
===========================================================
CRITICAL: This module is BROKEN. The agents can't connect to Vertex AI,
generate content, or work together. You need to fix it!

The infrastructure is here, but the intelligence is missing.
"""

import os
import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

# Google AI imports
from google import genai
from google.genai import types

# Internal imports
from ..models.legal_models import (
    LegalScenario,
    AnalysisReport,
    AgentResponse,
    ReportSection,
    TokenUsage
)
from ..prompts.personas import LegalPersonas
from .quality_validator import QualityValidator

logger = logging.getLogger(__name__)


class LegalIntelligenceAgent:
    """
    Main orchestrator for the Legal Intelligence AI System.

    CURRENT STATE: BROKEN
    - Can't connect to Vertex AI
    - Can't generate content
    - Can't chain context between agents

    YOUR MISSION: Fix the TODOs to make this system work!
    """

    def __init__(self, project_id: str, location: str = "us-central1", model_name: str = "gemini-2.0-flash"):
        """Initialize the Legal Intelligence Agent system."""
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.client = None
        self.model = None
        self.initialized = False

        # Components
        self.personas = LegalPersonas()
        self.quality_validator = QualityValidator()

        # Performance tracking
        self.token_usage_history = []
        self.processing_times = []
        self.success_count = 0
        self.total_attempts = 0

        # Configuration
        self.generation_config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
        )

        logger.info(f"LegalIntelligenceAgent initialized for project {project_id}")

    def initialize_vertex_ai(self) -> bool:
        """
        CURRENT STATE: Always returns False, can't connect to Vertex AI

        Requirements:
        1. Initialize Google Gen AI client with Vertex AI support
        2. Create a client instance configured for the project and location
        3. Test the connection with a simple prompt
        4. Handle errors gracefully and log them
        5. Set self.initialized = True if successful

        Hints:
        - Use genai.Client(vertexai=True, project=..., location=...)
        - Store the client in self.client
        - Test with client.models.generate_content()
        - Catch exceptions and log errors

        Expected imports are already included at the top of this file.
        """
        try:
            logger.info(f"Initializing Vertex AI for project: {self.project_id}")

            # Initialize Google Gen AI client with Vertex AI support
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
            logger.info(f"Vertex AI client created for project: {self.project_id}, location: {self.location}")

            # Create a model wrapper that uses the client internally
            # This provides the generate_content() interface expected by the rest of the code
            class ModelWrapper:
                def __init__(self, client, model_name):
                    self.client = client
                    self.model_name = model_name
                
                def generate_content(self, contents, config=None):
                    return self.client.models.generate_content(
                        model=self.model_name,
                        contents=contents,
                        config=config
                    )
            
            self.model = ModelWrapper(self.client, self.model_name)
            logger.info(f"Model wrapper created: {self.model_name}")

            # Test the connection with a simple prompt
            test_config = types.GenerateContentConfig(max_output_tokens=10)
            test_response = self.model.generate_content(
                contents="Say 'OK' if you're working",
                config=test_config
            )

            # Check the response
            if test_response and test_response.text:
                logger.info(f"Vertex AI connection test successful: {test_response.text[:50]}")
                self.initialized = True
                return True
            else:
                logger.error("Vertex AI connection test failed: No response text")
                self.initialized = False
                return False

        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
            self.initialized = False
            return False

    def generate_section_content(
        self,
        persona: str,
        section_type: str,
        scenario: LegalScenario,
        previous_sections: List[ReportSection] = None
    ) -> Tuple[str, TokenUsage, float]:
        """
        CURRENT STATE: Returns dummy content, no actual AI generation

        Requirements:
        1. Build a comprehensive prompt combining persona, scenario, and context
        2. Generate content using self.model with retry logic
        3. Track token usage from response.usage_metadata
        4. Calculate cost based on tokens
        5. Handle errors with exponential backoff

        Args:
            persona: The agent persona text (from personas.py)
            section_type: Type of section (e.g., "liability_assessment")
            scenario: The legal case to analyze
            previous_sections: Previous sections for context chaining

        Returns:
            Tuple of (content, token_usage, cost)

        Hints:
        - Use self._build_prompt() to create the prompt
        - Use self.model.generate_content() with self.generation_config
        - Implement retry with exponential backoff (2^attempt seconds)
        - Extract token counts from response.usage_metadata
        - Use self._calculate_cost() for cost calculation
        """
        if not self.initialized:
            raise RuntimeError("Agent system not initialized. Call initialize_vertex_ai() first.")

        start_time = time.time()
        previous_sections = previous_sections or []

        # Build the comprehensive prompt
        prompt = self._build_prompt(persona, section_type, scenario, previous_sections)

        # Implement content generation with retry logic
        max_retries = 3
        last_exception = None

        for attempt in range(max_retries):
            try:
                # Generate content using the model
                response = self.model.generate_content(
                    contents=prompt,
                    config=self.generation_config
                )

                # Extract text from response
                if not response or not hasattr(response, 'text') or not response.text:
                    raise ValueError("Empty or invalid response from model")

                content = response.text

                # Extract token usage from response.usage_metadata
                if not hasattr(response, 'usage_metadata') or not response.usage_metadata:
                    raise ValueError("Missing usage_metadata in response")

                usage_metadata = response.usage_metadata
                input_tokens = getattr(usage_metadata, 'prompt_token_count', 0)
                output_tokens = getattr(usage_metadata, 'candidates_token_count', 0)
                total_tokens = getattr(usage_metadata, 'total_token_count', input_tokens + output_tokens)

                # Create TokenUsage object
                token_usage = TokenUsage(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens
                )

                # Calculate cost
                cost = self._calculate_cost(token_usage)

                # Track token usage for statistics
                self.token_usage_history.append(token_usage)
                self.total_attempts += 1
                self.success_count += 1

                # Track processing time
                processing_time = time.time() - start_time
                self.processing_times.append(processing_time)

                logger.info(f"Successfully generated content for {section_type} (attempt {attempt + 1})")
                logger.debug(f"Tokens used: {total_tokens} (input: {input_tokens}, output: {output_tokens}), Cost: ${cost:.4f}")

                return content, token_usage, cost

            except Exception as e:
                last_exception = e
                self.total_attempts += 1
                
                if attempt < max_retries - 1:
                    # Exponential backoff: wait 2^attempt seconds
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Content generation failed for {section_type} (attempt {attempt + 1}/{max_retries}): {str(e)}. "
                        f"Retrying in {wait_time} seconds..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Content generation failed for {section_type} after {max_retries} attempts: {str(e)}")

        # If we get here, all retries failed
        raise RuntimeError(f"Failed to generate content for {section_type} after {max_retries} attempts: {str(last_exception)}")

    async def generate_complete_report(self, scenario: LegalScenario) -> AnalysisReport:
        """
        CURRENT STATE: Generates dummy report with no real analysis

        Requirements:
        1. Define section generation sequence with persona assignments
        2. Generate each section using generate_section_content()
        3. Pass previous sections for context chaining
        4. Validate quality and retry if below threshold
        5. Assemble final report with all sections

        The section sequence should be:
        - liability_assessment (business_analyst)
        - damage_calculation (business_analyst)
        - prior_art_analysis (market_researcher)
        - competitive_landscape (market_researcher)
        - risk_assessment (strategic_consultant)
        - strategic_recommendations (strategic_consultant)

        Hints:
        - Create section_config list with (section_type, persona) tuples
        - Use self.personas.get_persona() to get persona text
        - Pass sections list to generate_section_content for context
        - Use self.quality_validator.validate_section() to check quality
        - Retry with enhanced prompt if quality < 0.7
        """
        logger.info(f"Starting complete report generation for case: {scenario.case_name}")
        start_time = time.time()

        # Define section generation sequence with persona assignments
        section_config = [
            ("liability_assessment", "business_analyst"),
            ("damage_calculation", "business_analyst"),
            ("prior_art_analysis", "market_researcher"),
            ("competitive_landscape", "market_researcher"),
            ("risk_assessment", "strategic_consultant"),
            ("strategic_recommendations", "strategic_consultant")
        ]

        # Initialize sections list and tracking variables
        sections = []
        total_cost = 0.0
        total_tokens = 0
        quality_threshold = 0.7
        max_quality_retries = 2

        # Generate each section with context chaining
        for section_type, persona_type in section_config:
            logger.info(f"Generating section: {section_type} using {persona_type} persona")
            
            # Get persona text
            persona = self.personas.get_persona(persona_type)
            
            # Get expected elements for quality validation
            expected_elements = self._get_expected_elements(section_type)
            
            # Generate content with quality validation and retry
            content = None
            token_usage = None
            cost = 0.0
            quality_score = 0.0
            
            for quality_attempt in range(max_quality_retries + 1):
                try:
                    # Generate content using asyncio.to_thread to prevent blocking
                    content, token_usage, cost = await asyncio.to_thread(
                        self.generate_section_content,
                        persona=persona,
                        section_type=section_type,
                        scenario=scenario,
                        previous_sections=sections
                    )
                    
                    # Validate quality
                    quality_result = self.quality_validator.validate_section(
                        content=content,
                        section_type=section_type,
                        expected_elements=expected_elements
                    )
                    quality_score = quality_result.overall_score
                    
                    logger.info(f"Section {section_type} quality score: {quality_score:.2f}")
                    
                    # If quality meets threshold, break out of retry loop
                    if quality_score >= quality_threshold:
                        logger.info(f"Section {section_type} passed quality validation")
                        break
                    else:
                        if quality_attempt < max_quality_retries:
                            logger.warning(
                                f"Section {section_type} quality below threshold ({quality_score:.2f} < {quality_threshold}). "
                                f"Retrying... (attempt {quality_attempt + 1}/{max_quality_retries})"
                            )
                            # Add quality feedback to prompt for retry
                            feedback_text = "; ".join(quality_result.feedback)
                            persona = f"{persona}\n\nIMPORTANT: Previous attempt had quality issues. Please address: {feedback_text}"
                        else:
                            logger.warning(
                                f"Section {section_type} quality still below threshold after {max_quality_retries} retries. "
                                f"Proceeding with quality score: {quality_score:.2f}"
                            )
                
                except Exception as e:
                    logger.error(f"Error generating section {section_type}: {str(e)}")
                    if quality_attempt < max_quality_retries:
                        logger.info(f"Retrying section {section_type}...")
                        continue
                    else:
                        raise RuntimeError(f"Failed to generate section {section_type} after retries: {str(e)}")
            
            # Create ReportSection object
            section = ReportSection(
                type=section_type,
                title=self._get_section_title(section_type),
                content=content,
                agent_type=self._get_agent_type(persona),
                quality_score=quality_score,
                tokens_used=token_usage.total_tokens,
                cost=cost,
                timestamp=datetime.now().isoformat()
            )
            
            sections.append(section)
            total_cost += cost
            total_tokens += token_usage.total_tokens
            
            logger.info(f"Completed section {section_type}: {token_usage.total_tokens} tokens, ${cost:.4f} cost")
        
        # Calculate overall confidence score (average of section quality scores)
        confidence_score = sum(s.quality_score for s in sections) / len(sections) if sections else 0.0
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(sections, scenario)
        
        # Calculate total processing time
        processing_time = time.time() - start_time
        
        # Assemble final AnalysisReport
        report = AnalysisReport(
            scenario=scenario,
            sections=sections,
            executive_summary=executive_summary,
            total_cost=total_cost,
            total_tokens=total_tokens,
            processing_time=processing_time,
            confidence_score=confidence_score,
            timestamp=datetime.now().isoformat(),
            metadata={
                "sections_generated": len(sections),
                "average_quality": confidence_score,
                "generation_time": processing_time
            }
        )
        
        logger.info(
            f"Report generation complete: {len(sections)} sections, "
            f"{total_tokens} tokens, ${total_cost:.4f} cost, "
            f"confidence: {confidence_score:.2f}"
        )
        
        return report

    def _build_prompt(
        self,
        persona: str,
        section_type: str,
        scenario: LegalScenario,
        previous_sections: List[ReportSection]
    ) -> str:
        """Build a comprehensive prompt combining persona, context, and chain-of-thought instructions."""

        # Start with the persona
        prompt = persona + "\n\n"

        # Add chain-of-thought reasoning instructions
        prompt += """
REASONING INSTRUCTIONS:
You must use step-by-step reasoning to analyze this legal case. Structure your analysis as follows:
1. First, identify the key legal issues
2. Second, analyze the relevant facts
3. Third, apply legal principles
4. Finally, provide your conclusions

Think through each step carefully before moving to the next.
"""

        # Add context from previous sections if available
        if previous_sections:
            prompt += "\n\nPREVIOUS ANALYSIS:\n"
            for section in previous_sections[-2:]:  # Include last 2 sections for context
                prompt += f"\n{section.title}:\n"
                prompt += f"{section.content[:500]}...\n"  # Include summary

        # Add the specific task
        prompt += f"\n\nTASK: Provide a {section_type.replace('_', ' ')} for the following legal case:\n\n"

        # Add case details
        prompt += f"Case Name: {scenario.case_name}\n"
        prompt += f"Case Type: {scenario.case_type}\n"
        prompt += f"Key Issues: {', '.join(scenario.key_issues)}\n"
        prompt += f"Urgency: {scenario.urgency_level}\n\n"
        prompt += f"Complaint Summary:\n{scenario.complaint_text[:1500]}\n\n"

        # Add section-specific instructions
        prompt += self._get_section_instructions(section_type)

        return prompt

    def _get_section_instructions(self, section_type: str) -> str:
        """Get specific instructions for each section type."""
        instructions = {
            "liability_assessment": """
Analyze liability by:
- Identifying each potential claim
- Evaluating strength of evidence
- Assessing probability of success (use percentages)
- Citing relevant precedents or legal principles
""",
            "damage_calculation": """
Calculate potential damages by:
- Identifying categories of damages (actual, statutory, punitive)
- Providing specific dollar ranges
- Explaining calculation methodology
- Considering mitigation factors
""",
            "prior_art_analysis": """
Analyze prior art and precedents by:
- Identifying relevant existing patents/IP
- Assessing validity challenges
- Evaluating obviousness arguments
- Determining freedom to operate
""",
            "competitive_landscape": """
Analyze competitive implications by:
- Identifying key competitors affected
- Assessing market position changes
- Evaluating licensing opportunities
- Predicting competitor responses
""",
            "risk_assessment": """
Assess risks by:
- Identifying legal risks (probability and impact)
- Evaluating business risks
- Analyzing reputational risks
- Providing risk mitigation strategies
""",
            "strategic_recommendations": """
Provide strategic recommendations by:
- Outlining 3-5 specific action items
- Prioritizing by impact and urgency
- Estimating resource requirements
- Defining success metrics
"""
        }
        return instructions.get(section_type, "Provide comprehensive analysis for this section.")

    def _get_expected_elements(self, section_type: str) -> List[str]:
        """Get expected elements for quality validation."""
        elements_map = {
            "liability_assessment": ["claims", "evidence", "probability", "precedent"],
            "damage_calculation": ["damages", "calculation", "amount", "methodology"],
            "prior_art_analysis": ["patents", "prior art", "validity", "obviousness"],
            "competitive_landscape": ["competitors", "market", "position", "licensing"],
            "risk_assessment": ["risks", "probability", "impact", "mitigation"],
            "strategic_recommendations": ["recommendations", "action", "timeline", "resources"]
        }
        return elements_map.get(section_type, ["analysis", "assessment", "conclusion"])

    def _get_section_title(self, section_type: str) -> str:
        """Get formatted title for section."""
        titles = {
            "liability_assessment": "Liability Assessment",
            "damage_calculation": "Damage Calculation",
            "prior_art_analysis": "Prior Art Analysis",
            "competitive_landscape": "Competitive Landscape",
            "risk_assessment": "Risk Assessment",
            "strategic_recommendations": "Strategic Recommendations"
        }
        return titles.get(section_type, section_type.replace("_", " ").title())

    def _get_agent_type(self, persona: str) -> str:
        """Determine agent type from persona text."""
        if "Business Analyst" in persona:
            return "business_analyst"
        elif "Market Research" in persona:
            return "market_researcher"
        elif "Strategic" in persona:
            return "strategic_consultant"
        else:
            return "unknown"

    def _generate_executive_summary(self, sections: List[ReportSection], scenario: LegalScenario) -> str:
        """Generate executive summary from all sections."""
        summary = f"EXECUTIVE SUMMARY - {scenario.case_name}\n"
        summary += "=" * 50 + "\n\n"

        # Extract key points from each section
        for section in sections:
            # Get first substantive paragraph
            paragraphs = [p.strip() for p in section.content.split('\n\n') if len(p.strip()) > 50]
            if paragraphs:
                summary += f"{section.title}:\n"
                summary += f"{paragraphs[0][:200]}...\n\n"

        # Add overall assessment
        avg_quality = sum(s.quality_score for s in sections) / len(sections) if sections else 0
        summary += f"Overall Confidence: {avg_quality:.1%}\n"
        summary += f"Key Issues Identified: {len(scenario.key_issues)}\n"
        summary += f"Urgency Level: {scenario.urgency_level}\n"

        return summary

    def _calculate_cost(self, token_usage: TokenUsage) -> float:
        """Calculate cost based on token usage."""
        # Example pricing (adjust based on actual Vertex AI pricing)
        # Gemini pricing as of 2024: ~$0.00025 per 1K input tokens, ~$0.00125 per 1K output tokens
        input_cost = (token_usage.input_tokens / 1000) * 0.00025
        output_cost = (token_usage.output_tokens / 1000) * 0.00125
        return input_cost + output_cost

    # Metric tracking methods

    def get_token_usage_stats(self) -> Dict[str, Any]:
        """Get token usage statistics."""
        if not self.token_usage_history:
            return {"error": "No usage data available"}

        total_input = sum(u.input_tokens for u in self.token_usage_history)
        total_output = sum(u.output_tokens for u in self.token_usage_history)
        total_tokens = sum(u.total_tokens for u in self.token_usage_history)

        return {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_tokens,
            "average_per_request": total_tokens / len(self.token_usage_history) if self.token_usage_history else 0,
            "request_count": len(self.token_usage_history)
        }

    def get_avg_processing_time(self) -> float:
        """Get average processing time."""
        if not self.processing_times:
            return 0.0
        return sum(self.processing_times) / len(self.processing_times)

    def get_success_rate(self) -> float:
        """Get success rate of generations."""
        if self.total_attempts == 0:
            return 0.0
        return self.success_count / self.total_attempts