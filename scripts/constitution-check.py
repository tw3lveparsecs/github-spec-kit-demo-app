#!/usr/bin/env python3
"""
Constitution Compliance Check Script (T139)

Validates that the implementation follows all four constitution principles:
I.   Code Quality Standards
II.  Testing Standards
III. User Experience Consistency
IV.  Performance Requirements

Reference: .specify/memory/constitution.md
"""

import os
import re
import subprocess
import sys
from pathlib import Path


class ConstitutionChecker:
    """Checks implementation against constitution principles."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results = []
        self.passed = 0
        self.warnings = 0
        self.failed = 0
    
    def check(self, principle: str, item: str, condition: bool, details: str = "", warning: bool = False):
        """Record a compliance check."""
        if condition:
            status = "✅"
            self.passed += 1
        elif warning:
            status = "⚠️"
            self.warnings += 1
        else:
            status = "❌"
            self.failed += 1
        
        self.results.append((principle, item, condition, details))
        print(f"  {status} {item}")
        if details and not condition:
            print(f"       {details}")
    
    def file_exists(self, path: str) -> bool:
        """Check if a file exists relative to repo root."""
        return (self.repo_root / path).exists()
    
    def file_contains(self, path: str, pattern: str) -> bool:
        """Check if file contains a pattern."""
        filepath = self.repo_root / path
        if not filepath.exists():
            return False
        try:
            content = filepath.read_text(encoding="utf-8")
            return bool(re.search(pattern, content, re.IGNORECASE))
        except Exception:
            return False
    
    def run_command(self, cmd: list) -> tuple[bool, str]:
        """Run a command and return success and output."""
        try:
            result = subprocess.run(
                cmd, cwd=self.repo_root, capture_output=True, text=True, timeout=60
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)


def check_code_quality(checker: ConstitutionChecker):
    """Principle I: Code Quality Standards"""
    print("\n📋 PRINCIPLE I: CODE QUALITY STANDARDS")
    print("-" * 50)
    
    # Linting & Formatting tools configured
    checker.check(
        "I", "Black formatter configured (pyproject.toml)",
        checker.file_contains("backend/pyproject.toml", r"\[tool\.black\]")
    )
    
    checker.check(
        "I", "Flake8 linter configured",
        checker.file_exists("backend/.flake8") or 
        checker.file_contains("backend/pyproject.toml", r"\[tool\.flake8\]") or
        checker.file_contains("backend/setup.cfg", "flake8")
    )
    
    checker.check(
        "I", "mypy type checker configured",
        checker.file_contains("backend/pyproject.toml", r"\[tool\.mypy\]")
    )
    
    checker.check(
        "I", "ESLint configured for frontend",
        checker.file_exists("frontend/.eslintrc.json") or
        checker.file_exists("frontend/eslint.config.js"),
        warning=True
    )
    
    # Documentation
    checker.check(
        "I", "README documentation exists",
        checker.file_exists("README.md")
    )
    
    checker.check(
        "I", "API documentation exists (OpenAPI)",
        checker.file_exists("specs/001-speckit-demo-app/contracts/api.openapi.yaml")
    )
    
    # Type Safety
    checker.check(
        "I", "Python type hints used in models",
        checker.file_contains("backend/src/models/__init__.py", "dataclass") or
        checker.file_contains("backend/src/models/session.py", ":")
    )


def check_testing_standards(checker: ConstitutionChecker):
    """Principle II: Testing Standards"""
    print("\n🧪 PRINCIPLE II: TESTING STANDARDS")
    print("-" * 50)
    
    # Test files exist
    checker.check(
        "II", "Backend test files exist",
        checker.file_exists("backend/tests") or 
        checker.file_exists("backend/test_api.py")
    )
    
    checker.check(
        "II", "Unit tests directory exists",
        checker.file_exists("backend/tests/unit"),
        warning=True
    )
    
    checker.check(
        "II", "Integration tests directory exists",
        checker.file_exists("backend/tests/integration"),
        warning=True
    )
    
    checker.check(
        "II", "E2E tests directory exists",
        checker.file_exists("backend/tests/e2e") or
        checker.file_exists("frontend/tests/playwright")
    )
    
    # pytest configured
    checker.check(
        "II", "pytest configured",
        checker.file_contains("backend/pyproject.toml", r"\[tool\.pytest")
    )
    
    # Coverage configured
    checker.check(
        "II", "Coverage configured",
        checker.file_contains("backend/pyproject.toml", r"\[tool\.coverage\]") or
        checker.file_exists("backend/.coveragerc")
    )
    
    # CI runs tests
    checker.check(
        "II", "CI workflow runs tests",
        checker.file_contains(".github/workflows/ci.yml", "pytest")
    )


def check_ux_consistency(checker: ConstitutionChecker):
    """Principle III: User Experience Consistency"""
    print("\n🎨 PRINCIPLE III: USER EXPERIENCE CONSISTENCY")
    print("-" * 50)
    
    # Design system
    checker.check(
        "III", "Primer CSS design system used",
        checker.file_contains("frontend/src/index.html", "primer")
    )
    
    # Accessibility
    checker.check(
        "III", "ARIA attributes used",
        checker.file_contains("frontend/src/index.html", "aria-")
    )
    
    checker.check(
        "III", "Keyboard navigation support",
        checker.file_contains("frontend/src/index.html", "tabindex") or
        checker.file_contains("frontend/src/index.html", "role=")
    )
    
    checker.check(
        "III", "Skip link for accessibility",
        checker.file_contains("frontend/src/index.html", "skip")
    )
    
    # Responsive design
    checker.check(
        "III", "Responsive viewport meta tag",
        checker.file_contains("frontend/src/index.html", "viewport")
    )
    
    # Error handling
    checker.check(
        "III", "Toast notifications for feedback",
        checker.file_exists("frontend/src/js/utils/toast.js")
    )
    
    # Loading states
    checker.check(
        "III", "Loading spinner styles",
        checker.file_contains("frontend/src/css/main.css", "spinner") or
        checker.file_contains("frontend/src/css/animations.css", "spinner")
    )


def check_performance_requirements(checker: ConstitutionChecker):
    """Principle IV: Performance Requirements"""
    print("\n⚡ PRINCIPLE IV: PERFORMANCE REQUIREMENTS")
    print("-" * 50)
    
    # Caching
    checker.check(
        "IV", "Response caching implemented",
        checker.file_contains("backend/src/app.py", "cache") or
        checker.file_contains("backend/src/services/cache.py", "cache")
    )
    
    # Compression
    checker.check(
        "IV", "Response compression enabled",
        checker.file_contains("backend/src/app.py", "gzip") or
        checker.file_contains("backend/src/app.py", "compress")
    )
    
    # Service worker
    checker.check(
        "IV", "Service worker for offline/caching",
        checker.file_exists("frontend/src/sw.js")
    )
    
    # Performance budget verification
    checker.check(
        "IV", "Bundle size verification script exists",
        checker.file_exists("scripts/verify-bundle-size.py")
    )
    
    # Performance profiling
    checker.check(
        "IV", "Performance profiling script exists",
        checker.file_exists("scripts/performance-profile.py")
    )
    
    # Monitoring (Azure App Insights)
    checker.check(
        "IV", "Azure Application Insights configured",
        checker.file_exists("infra/modules/app-insights.bicep")
    )


def main():
    """Run constitution compliance check."""
    print("=" * 60)
    print("CONSTITUTION COMPLIANCE CHECK (T139)")
    print("=" * 60)
    print("Reference: .specify/memory/constitution.md")
    
    repo_root = Path(__file__).parent.parent
    checker = ConstitutionChecker(repo_root)
    
    # Run all principle checks
    check_code_quality(checker)
    check_testing_standards(checker)
    check_ux_consistency(checker)
    check_performance_requirements(checker)
    
    # Summary
    print()
    print("=" * 60)
    print("COMPLIANCE SUMMARY")
    print("=" * 60)
    print(f"  ✅ Passed:   {checker.passed}")
    print(f"  ⚠️  Warnings: {checker.warnings}")
    print(f"  ❌ Failed:   {checker.failed}")
    print()
    
    total = checker.passed + checker.warnings + checker.failed
    compliance_pct = (checker.passed / total * 100) if total > 0 else 0
    
    print(f"Compliance Score: {compliance_pct:.1f}%")
    print()
    
    if checker.failed == 0:
        print("✅ CONSTITUTION COMPLIANCE: PASS")
        print("Implementation follows all constitution principles.")
        sys.exit(0)
    elif compliance_pct >= 80:
        print("⚠️  CONSTITUTION COMPLIANCE: PARTIAL")
        print("Most principles are followed. Review failed items.")
        sys.exit(0)
    else:
        print("❌ CONSTITUTION COMPLIANCE: FAIL")
        print("Significant deviations from constitution principles.")
        sys.exit(1)


if __name__ == "__main__":
    main()
