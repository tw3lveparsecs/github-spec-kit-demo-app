"""
Constitution service for parsing and managing Spec Kit constitution rules.
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from models.constitution import ConstitutionPrinciple, ConstitutionCheck, ConstitutionViolation

logger = logging.getLogger(__name__)


@dataclass
class ConstitutionRule:
    """
    A single constitution rule with its details.
    """

    rule_id: str
    category: str
    title: str
    description: str
    examples: List[str]
    enforcement_level: str  # "required", "recommended", "optional"


class ConstitutionService:
    """
    Service for loading and managing Spec Kit constitution rules.
    """

    def __init__(self, constitution_path: Optional[Path] = None):
        """
        Initialize the constitution service.

        Args:
            constitution_path: Path to constitution.md file. If None, uses default location.
        """
        if constitution_path is None:
            constitution_path = (
                Path(__file__).parent.parent.parent.parent / "specs" / "constitution.md"
            )

        self.constitution_path = constitution_path
        self._rules: Dict[str, ConstitutionRule] = {}
        self._loaded = False

    def load_constitution(self) -> None:
        """
        Load and parse the constitution.md file.

        Raises:
            FileNotFoundError: If constitution file doesn't exist.
        """
        if self._loaded:
            return

        if not self.constitution_path.exists():
            logger.warning(f"Constitution file not found: {self.constitution_path}")
            return

        logger.info(f"Loading constitution from {self.constitution_path}")

        # For MVP, just verify the file exists
        # Full parsing will be implemented in Phase 5 (User Story 3)
        with open(self.constitution_path, "r", encoding="utf-8") as f:
            content = f.read()
            logger.info(f"Constitution loaded: {len(content)} characters")

        self._loaded = True

    def get_rules(self) -> List[ConstitutionRule]:
        """
        Get all constitution rules.

        Returns:
            List of all loaded constitution rules.
        """
        if not self._loaded:
            self.load_constitution()

        return list(self._rules.values())

    def get_rule_by_id(self, rule_id: str) -> Optional[ConstitutionRule]:
        """
        Get a specific constitution rule by ID.

        Args:
            rule_id: The rule identifier.

        Returns:
            The rule if found, None otherwise.
        """
        if not self._loaded:
            self.load_constitution()

        return self._rules.get(rule_id)

    def get_rules_by_category(self, category: str) -> List[ConstitutionRule]:
        """
        Get all rules in a specific category.

        Args:
            category: The category name (e.g., "documentation", "testing", "performance").

        Returns:
            List of rules in the specified category.
        """
        if not self._loaded:
            self.load_constitution()

        return [rule for rule in self._rules.values() if rule.category == category]

    def get_principles(self) -> List[ConstitutionPrinciple]:
        """
        Get all constitution principles as structured ConstitutionPrinciple objects.
        
        For the demo, returns 4 pre-defined principles representing core quality standards.
        
        Returns:
            List of ConstitutionPrinciple objects.
        """
        if not self._loaded:
            self.load_constitution()
        
        # Define the 4 core demo principles
        principles = [
            ConstitutionPrinciple(
                principle_id="performance",
                title="Performance Optimization",
                description="All implementations must prioritize response time and resource efficiency. "
                           "This includes lazy loading, caching strategies, and optimized database queries.",
                category="technical",
                priority=1,
                examples=[
                    "API endpoints should respond within 200ms",
                    "Use pagination for large datasets",
                    "Implement caching for frequently accessed data",
                    "Optimize bundle size for frontend assets"
                ]
            ),
            ConstitutionPrinciple(
                principle_id="security",
                title="Security Best Practices",
                description="Security is non-negotiable. All features must implement proper authentication, "
                           "authorization, input validation, and data protection measures.",
                category="security",
                priority=1,
                examples=[
                    "Validate all user inputs",
                    "Use parameterized queries to prevent SQL injection",
                    "Implement proper CORS policies",
                    "Never expose sensitive data in logs or responses"
                ]
            ),
            ConstitutionPrinciple(
                principle_id="maintainability",
                title="Code Maintainability",
                description="Code should be written for humans first. This means clear naming, "
                           "proper documentation, and adherence to established patterns.",
                category="maintainability",
                priority=2,
                examples=[
                    "Follow established coding conventions",
                    "Write comprehensive docstrings",
                    "Keep functions focused and small",
                    "Use meaningful variable names"
                ]
            ),
            ConstitutionPrinciple(
                principle_id="user-experience",
                title="User Experience",
                description="Every feature should provide a seamless user experience with clear feedback, "
                           "intuitive interactions, and accessibility compliance.",
                category="user-experience",
                priority=2,
                examples=[
                    "Provide loading states for async operations",
                    "Show meaningful error messages",
                    "Ensure keyboard navigation works",
                    "Support screen readers with proper ARIA labels"
                ]
            )
        ]
        
        return principles

    def evaluate_checks(self, artifact_content: str, artifact_type: str) -> List[ConstitutionCheck]:
        """
        Evaluate constitution checks against an artifact.
        
        This simulates the AI-powered constitution validation that would occur
        during the real Spec Kit workflow. For the demo, it returns pre-defined
        check results to illustrate the concept.
        
        Args:
            artifact_content: The markdown content of the artifact.
            artifact_type: Type of artifact (plan, spec, tasks, implement).
            
        Returns:
            List of ConstitutionCheck objects with evaluation results.
        """
        from datetime import datetime
        import uuid
        
        checks = []
        
        # Simulate checks for a plan artifact
        if artifact_type == "plan":
            # Performance check - passes
            perf_check = ConstitutionCheck(
                check_id=f"check-{uuid.uuid4().hex[:8]}",
                principle_id="performance",
                artifact_type=artifact_type,
                check_name="Performance Requirements Defined",
                check_description="Verifies that performance targets are specified in the implementation plan.",
                status="passed",
                evaluated_at=datetime.utcnow(),
                violations=[]
            )
            checks.append(perf_check)
            
            # Security check - warning
            sec_check = ConstitutionCheck(
                check_id=f"check-{uuid.uuid4().hex[:8]}",
                principle_id="security",
                artifact_type=artifact_type,
                check_name="Security Considerations Documented",
                check_description="Verifies that security measures are outlined in the plan.",
                status="warning",
                evaluated_at=datetime.utcnow(),
                violations=[
                    ConstitutionViolation(
                        violation_id=f"viol-{uuid.uuid4().hex[:8]}",
                        check_id="",  # Will be updated
                        severity="medium",
                        message="Authentication flow should explicitly mention token refresh strategy.",
                        location="Security Considerations section",
                        recommendation="Add details about JWT refresh token handling and expiration policies."
                    )
                ]
            )
            sec_check.violations[0].check_id = sec_check.check_id
            checks.append(sec_check)
            
            # Maintainability check - passes
            maint_check = ConstitutionCheck(
                check_id=f"check-{uuid.uuid4().hex[:8]}",
                principle_id="maintainability",
                artifact_type=artifact_type,
                check_name="Code Structure Defined",
                check_description="Verifies that folder structure and coding patterns are specified.",
                status="passed",
                evaluated_at=datetime.utcnow(),
                violations=[]
            )
            checks.append(maint_check)
            
            # UX check - passes
            ux_check = ConstitutionCheck(
                check_id=f"check-{uuid.uuid4().hex[:8]}",
                principle_id="user-experience",
                artifact_type=artifact_type,
                check_name="User Flow Documented",
                check_description="Verifies that user interactions are documented with appropriate feedback.",
                status="passed",
                evaluated_at=datetime.utcnow(),
                violations=[]
            )
            checks.append(ux_check)
        
        logger.info(f"Evaluated {len(checks)} constitution checks for {artifact_type}")
        return checks

    def get_check_summary(self, checks: List[ConstitutionCheck]) -> Dict:
        """
        Get a summary of check results.
        
        Args:
            checks: List of ConstitutionCheck objects.
            
        Returns:
            Dictionary with counts of passed, failed, warning checks.
        """
        summary = {
            "total": len(checks),
            "passed": sum(1 for c in checks if c.status == "passed"),
            "failed": sum(1 for c in checks if c.status == "failed"),
            "warning": sum(1 for c in checks if c.status == "warning"),
            "not_run": sum(1 for c in checks if c.status == "not_run"),
            "overall_status": "passed"
        }
        
        if summary["failed"] > 0:
            summary["overall_status"] = "failed"
        elif summary["warning"] > 0:
            summary["overall_status"] = "warning"
        
        return summary
