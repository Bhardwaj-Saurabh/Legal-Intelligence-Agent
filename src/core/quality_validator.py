"""
Quality Validation System for Legal Intelligence AI
===================================================
CRITICAL: The quality validation algorithms are BROKEN!
Without proper scoring, we can't tell if the AI output is any good.

Your mission: Implement the scoring algorithms in TODOs 4 and 5.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import statistics

from ..models.legal_models import AnalysisReport, ReportSection

logger = logging.getLogger(__name__)


@dataclass
class QualityScore:
    """Quality score with detailed breakdown."""
    overall_score: float
    coherence_score: float
    groundedness_score: float
    completeness_score: float
    structure_score: float
    feedback: List[str]


@dataclass
class ValidationResult:
    """Validation result for a report."""
    overall_score: float
    passed: bool
    section_scores: Dict[str, float]
    issues: List[str]
    recommendations: List[str]


class QualityValidator:
    """
    Validates the quality of AI-generated legal analysis.

    CURRENT STATE: BROKEN
    - Coherence scoring always returns 0
    - Groundedness scoring always returns 0
    - Can't properly validate content quality

    YOUR MISSION: Fix TODOs 4 and 5 to make validation work!
    """

    def __init__(self, min_quality_threshold: float = 0.7):
        """Initialize the quality validator."""
        self.min_quality_threshold = min_quality_threshold
        self.validation_history = []

    def validate_section(
        self,
        content: str,
        section_type: str,
        expected_elements: List[str]
    ) -> QualityScore:
        """Validate a single report section."""

        # Calculate individual scores
        coherence = self.calculate_coherence_score(content, section_type)
        groundedness = self.calculate_groundedness_score(content, section_type, expected_elements)
        completeness = self._calculate_completeness_score(content, expected_elements)
        structure = self._calculate_structure_score(content)

        # Calculate overall score (weighted average)
        overall = (
            coherence * 0.3 +
            groundedness * 0.3 +
            completeness * 0.25 +
            structure * 0.15
        )

        # Generate feedback
        feedback = []
        if coherence < 0.7:
            feedback.append("Improve logical flow and use more transition phrases")
        if groundedness < 0.7:
            feedback.append(f"Include more {section_type}-specific terminology and evidence")
        if completeness < 0.7:
            feedback.append(f"Address all expected elements: {', '.join(expected_elements)}")
        if structure < 0.7:
            feedback.append("Improve paragraph structure and organization")

        return QualityScore(
            overall_score=overall,
            coherence_score=coherence,
            groundedness_score=groundedness,
            completeness_score=completeness,
            structure_score=structure,
            feedback=feedback
        )

    def calculate_coherence_score(self, content: str, section_type: str) -> float:
        """
        Calculate coherence score for the content.

        Scores coherence from 0.0 to 1.0 based on:
        1. Paragraph structure (check for multiple paragraphs)
        2. Logical connectors (therefore, however, furthermore, etc.)
        3. Structured thinking (first, second, finally, etc.)
        4. Content depth (adequate number of sentences)

        Scoring distribution:
        - Multiple paragraphs: +0.3 points
        - Logical connectors present: +0.2 points
        - Structured presentation: +0.2 points
        - Adequate detail (8+ sentences): +0.3 points

        Args:
            content: The text to analyze
            section_type: Type of section (for context)

        Returns:
            Float between 0.0 and 1.0 representing coherence
        """
        score = 0.0
        content_lower = content.lower()

        # 1. Check paragraph structure (split by '\n\n')
        paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 0]
        if len(paragraphs) >= 3:
            score += 0.3
        elif len(paragraphs) >= 2:
            score += 0.2
        elif len(paragraphs) >= 1:
            score += 0.1

        # 2. Count logical connectors
        logical_connectors = [
            'therefore', 'however', 'furthermore', 'moreover', 'consequently',
            'additionally', 'thus', 'hence', 'accordingly', 'nevertheless',
            'nonetheless', 'meanwhile', 'subsequently', 'alternatively',
            'specifically', 'particularly', 'notably', 'indeed', 'in fact',
            'for example', 'for instance', 'in addition', 'on the other hand',
            'as a result', 'in conclusion', 'in summary', 'overall'
        ]
        
        connector_count = sum(1 for connector in logical_connectors if connector in content_lower)
        if connector_count >= 5:
            score += 0.2
        elif connector_count >= 3:
            score += 0.15
        elif connector_count >= 1:
            score += 0.1

        # 3. Check for structured thinking markers
        structure_markers = [
            'first', 'second', 'third', 'fourth', 'fifth',
            'initially', 'subsequently', 'finally', 'lastly',
            'next', 'then', 'afterward', 'previously',
            'step 1', 'step 2', 'step 3',
            '1.', '2.', '3.', '4.', '5.',
            'one', 'two', 'three', 'four', 'five'
        ]
        
        structure_count = sum(1 for marker in structure_markers if marker in content_lower)
        if structure_count >= 3:
            score += 0.2
        elif structure_count >= 2:
            score += 0.15
        elif structure_count >= 1:
            score += 0.1

        # 4. Measure content depth (sentence count)
        # Split by sentence-ending punctuation, filter out empty strings
        sentences = [s.strip() for s in content.replace('!', '.').replace('?', '.').split('.') 
                    if len(s.strip()) > 10]  # Filter out very short fragments
        
        sentence_count = len(sentences)
        if sentence_count >= 12:
            score += 0.3
        elif sentence_count >= 8:
            score += 0.25
        elif sentence_count >= 5:
            score += 0.15
        elif sentence_count >= 3:
            score += 0.1

        # Cap the final score at 1.0
        return min(score, 1.0)

    def calculate_groundedness_score(
        self,
        content: str,
        section_type: str,
        expected_elements: List[str]
    ) -> float:
        """
        CURRENT STATE: Always returns 0.0 - no groundedness checking!

        Requirements:
        Implement an algorithm that scores groundedness from 0.0 to 1.0 based on:
        1. Section-specific keyword presence
        2. Evidence-based reasoning indicators
        3. Coverage of expected elements

        For each section_type, check for relevant keywords:
        - liability_assessment: liability, negligence, breach, duty, causation, etc.
        - damage_calculation: damages, compensation, calculation, quantum, etc.
        - prior_art_analysis: prior art, patent, novelty, obviousness, etc.
        - competitive_landscape: competitors, market share, positioning, etc.
        - risk_assessment: risk, probability, impact, mitigation, etc.
        - strategic_recommendations: recommendation, strategy, implementation, etc.

        Scoring distribution (suggested):
        - Keyword coverage: up to 0.4 points
        - Reasoning indicators: up to 0.3 points
        - Expected elements coverage: up to 0.3 points

        Args:
            content: The text to analyze
            section_type: Type of section for keyword selection
            expected_elements: List of elements that should be present

        Returns:
            Float between 0.0 and 1.0 representing groundedness

        Hints:
        - Create a dictionary mapping section_type to relevant keywords
        - Count how many keywords appear in the content
        - Look for reasoning phrases like "based on", "because", "due to"
        - Check coverage of expected_elements list
        - Cap the final score at 1.0
        """
        score = 0.0
        content_lower = content.lower()

        # 1. Define section-specific keywords dictionary
        section_keywords = {
            "liability_assessment": [
                'liability', 'negligence', 'breach', 'duty', 'causation', 'fault',
                'responsibility', 'obligation', 'standard of care', 'proximate cause',
                'tort', 'wrongful', 'violation', 'infringement', 'claim', 'defendant',
                'plaintiff', 'merit', 'evidence', 'precedent', 'case law'
            ],
            "damage_calculation": [
                'damages', 'compensation', 'calculation', 'quantum', 'loss', 'injury',
                'harm', 'economic loss', 'lost profits', 'punitive', 'actual damages',
                'statutory damages', 'restitution', 'recovery', 'award', 'settlement',
                'monetary', 'financial impact', 'cost', 'expense', 'revenue'
            ],
            "prior_art_analysis": [
                'prior art', 'patent', 'novelty', 'obviousness', 'invention', 'claims',
                'validity', 'infringement', 'patentability', 'non-obvious', 'prior',
                'existing', 'publication', 'disclosure', 'freedom to operate', 'f-to',
                'patent search', 'art', 'reference', 'prior publication'
            ],
            "competitive_landscape": [
                'competitors', 'market share', 'positioning', 'competitive', 'market',
                'industry', 'rival', 'competition', 'advantage', 'disadvantage',
                'market position', 'market leader', 'niche', 'differentiation',
                'competitive advantage', 'market analysis', 'competitive analysis',
                'market dynamics', 'market trends', 'market size'
            ],
            "risk_assessment": [
                'risk', 'probability', 'impact', 'mitigation', 'threat', 'vulnerability',
                'exposure', 'likelihood', 'consequence', 'severity', 'uncertainty',
                'hazard', 'peril', 'danger', 'challenge', 'concern', 'issue',
                'risk management', 'risk analysis', 'risk factor', 'risk level'
            ],
            "strategic_recommendations": [
                'recommendation', 'strategy', 'implementation', 'action', 'plan',
                'approach', 'tactic', 'initiative', 'measure', 'step', 'course of action',
                'proposal', 'suggestion', 'guidance', 'direction', 'roadmap', 'timeline',
                'milestone', 'objective', 'goal', 'priority'
            ]
        }

        # 2. Get keywords for this section_type
        keywords = section_keywords.get(section_type, [])
        
        # 3. Calculate keyword coverage (up to 0.4 points)
        if keywords:
            found_keywords = sum(1 for keyword in keywords if keyword.lower() in content_lower)
            keyword_coverage = found_keywords / len(keywords)
            
            # Score based on coverage percentage
            if keyword_coverage >= 0.5:  # 50% or more keywords found
                score += 0.4
            elif keyword_coverage >= 0.3:  # 30-49% keywords found
                score += 0.3
            elif keyword_coverage >= 0.2:  # 20-29% keywords found
                score += 0.2
            elif keyword_coverage >= 0.1:  # 10-19% keywords found
                score += 0.1
            # Less than 10% gets 0 points

        # 4. Check for reasoning indicators (up to 0.3 points)
        reasoning_phrases = [
            'based on', 'because', 'due to', 'as a result', 'according to',
            'evidence shows', 'the evidence', 'research indicates', 'studies show',
            'data suggests', 'analysis reveals', 'findings indicate', 'demonstrates',
            'establishes', 'proves', 'supports', 'indicates', 'suggests', 'reveals',
            'shows that', 'indicates that', 'suggests that', 'demonstrates that',
            'according to the', 'in light of', 'given that', 'considering',
            'taking into account', 'in view of', 'on the basis of'
        ]
        
        reasoning_count = sum(1 for phrase in reasoning_phrases if phrase in content_lower)
        if reasoning_count >= 5:
            score += 0.3
        elif reasoning_count >= 4:
            score += 0.25
        elif reasoning_count >= 3:
            score += 0.2
        elif reasoning_count >= 2:
            score += 0.15
        elif reasoning_count >= 1:
            score += 0.1

        # 5. Check expected elements coverage (up to 0.3 points)
        if expected_elements:
            # Check for both exact matches and partial matches (e.g., "recommend" matches "recommendation")
            covered_elements = 0
            for element in expected_elements:
                element_lower = element.lower()
                # Check for exact match
                if element_lower in content_lower:
                    covered_elements += 1
                else:
                    # Check for partial matches - if element root word appears in content
                    # e.g., "recommend" should match "recommendation"
                    element_root = element_lower.rstrip('ation').rstrip('ing').rstrip('s')
                    if len(element_root) >= 4:  # Only check if root is substantial
                        if element_root in content_lower:
                            covered_elements += 1
            
            element_coverage = covered_elements / len(expected_elements)
            
            # Score based on coverage percentage
            if element_coverage >= 1.0:  # All elements found
                score += 0.3
            elif element_coverage >= 0.75:  # 75-99% elements found
                score += 0.25
            elif element_coverage >= 0.5:  # 50-74% elements found
                score += 0.2
            elif element_coverage >= 0.25:  # 25-49% elements found
                score += 0.15
            elif element_coverage > 0:  # 1-24% elements found
                score += 0.1
            # 0% gets 0 points

        # 6. Cap the final score at 1.0
        return min(score, 1.0)

    def _calculate_completeness_score(self, content: str, expected_elements: List[str]) -> float:
        """Calculate how completely the content addresses requirements."""
        if not expected_elements:
            # If no specific elements expected, check general completeness
            word_count = len(content.split())
            if word_count >= 200:
                return 1.0
            elif word_count >= 100:
                return 0.7
            elif word_count >= 50:
                return 0.5
            else:
                return 0.3

        # Check coverage of expected elements
        content_lower = content.lower()
        covered_elements = sum(1 for element in expected_elements
                             if element.lower() in content_lower)

        coverage_ratio = covered_elements / len(expected_elements)

        # Also consider content length
        word_count = len(content.split())
        length_score = min(word_count / 200, 1.0)  # Expect at least 200 words

        # Combined score
        return (coverage_ratio * 0.7) + (length_score * 0.3)

    def _calculate_structure_score(self, content: str) -> float:
        """Calculate structural quality of the content."""
        score = 0.0

        # Check for paragraphs
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 3:
            score += 0.3
        elif len(paragraphs) >= 2:
            score += 0.2
        elif len(paragraphs) >= 1:
            score += 0.1

        # Check for lists or bullet points
        has_lists = any(marker in content for marker in ['•', '-', '*', '1.', '2.', '3.'])
        if has_lists:
            score += 0.2

        # Check for headers or emphasized text
        has_headers = any(line.isupper() or line.startswith('#')
                        for line in content.split('\n') if len(line.strip()) > 0)
        if has_headers:
            score += 0.1

        # Check sentence variety
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 10]
        if len(sentences) >= 3:
            sentence_lengths = [len(s.split()) for s in sentences]
            if len(set(sentence_lengths)) >= 3:  # Variety in sentence length
                score += 0.2

        # Check for conclusion indicators
        conclusion_indicators = ['conclusion', 'summary', 'therefore', 'in summary', 'overall']
        has_conclusion = any(indicator in content.lower() for indicator in conclusion_indicators)
        if has_conclusion:
            score += 0.2

        return min(score, 1.0)

    def validate_report(self, report: AnalysisReport) -> ValidationResult:
        """Validate a complete report."""
        section_scores = {}
        all_issues = []
        all_recommendations = []

        # Validate each section
        for section in report.sections:
            expected_elements = self._get_expected_elements_for_section(section.type)
            quality = self.validate_section(
                content=section.content,
                section_type=section.type,
                expected_elements=expected_elements
            )

            section_scores[section.type] = quality.overall_score

            # Collect issues and recommendations
            if quality.overall_score < self.min_quality_threshold:
                all_issues.append(f"{section.title}: Score {quality.overall_score:.2f} below threshold")
                all_recommendations.extend(quality.feedback)

        # Calculate overall score
        overall_score = statistics.mean(section_scores.values()) if section_scores else 0.0

        # Determine if report passes
        passed = overall_score >= self.min_quality_threshold

        # Store in history
        self.validation_history.append({
            "timestamp": report.timestamp,
            "overall_score": overall_score,
            "passed": passed
        })

        return ValidationResult(
            overall_score=overall_score,
            passed=passed,
            section_scores=section_scores,
            issues=all_issues,
            recommendations=all_recommendations[:5]  # Top 5 recommendations
        )

    def _get_expected_elements_for_section(self, section_type: str) -> List[str]:
        """Get expected elements for a section type."""
        elements_map = {
            "liability_assessment": ["liability", "breach", "duty", "causation"],
            "damage_calculation": ["damages", "calculation", "compensation", "quantum"],
            "prior_art_analysis": ["prior art", "patent", "novelty", "claims"],
            "competitive_landscape": ["competitors", "market", "positioning", "advantage"],
            "risk_assessment": ["risk", "probability", "impact", "mitigation"],
            "strategic_recommendations": ["recommendation", "strategy", "implementation", "timeline"]
        }
        return elements_map.get(section_type, ["analysis", "assessment"])

    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get quality metrics from validation history."""
        if not self.validation_history:
            return {"error": "No validation history available"}

        recent = self.validation_history[-10:]  # Last 10 validations

        return {
            "total_validations": len(self.validation_history),
            "recent_average_score": statistics.mean([v["overall_score"] for v in recent]),
            "recent_pass_rate": sum(1 for v in recent if v["passed"]) / len(recent),
            "threshold": self.min_quality_threshold
        }