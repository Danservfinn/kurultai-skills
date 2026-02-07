"""
Tests for horde-prompt prompt generation.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts import generate_prompt, list_agents, validate_prompt, score_task_complexity


class TestPromptGeneration:
    """Test prompt generation functionality."""

    def test_generate_basic_prompt(self):
        """Test basic prompt generation."""
        result = generate_prompt(
            task="Design a REST API",
            agent_type="backend-architect"
        )

        assert result.prompt
        assert result.estimated_tokens > 0
        assert result.agent_tier == "implementation"
        assert result.compression_ratio < 1.0

    def test_minimal_token_budget(self):
        """Test minimal token budget produces shorter prompts."""
        result_minimal = generate_prompt(
            task="Design a REST API",
            agent_type="backend-architect",
            token_budget="minimal"
        )
        result_verbose = generate_prompt(
            task="Design a REST API",
            agent_type="backend-architect",
            token_budget="verbose"
        )

        assert result_minimal.estimated_tokens < result_verbose.estimated_tokens
        assert "ROLE:" in result_minimal.prompt
        assert "compact_syntax" in result_minimal.optimizations_applied

    def test_pattern_injection(self):
        """Test pattern protocol injection."""
        result = generate_prompt(
            task="Review this code",
            agent_type="security-auditor",
            pattern="review-loop"
        )

        assert "REVIEW LOOP" in result.prompt
        assert "pattern_review-loop" in result.optimizations_applied

    def test_unknown_agent_type_raises_error(self):
        """Test that unknown agent types raise ValueError."""
        with pytest.raises(ValueError, match="Unknown agent type"):
            generate_prompt(
                task="Some task",
                agent_type="nonexistent-agent"
            )

    def test_anti_sycophancy_for_judgment_agents(self):
        """Test that judgment agents get anti-sycophancy instructions."""
        result = generate_prompt(
            task="Evaluate costs",
            agent_type="cost-analyst",
            token_budget="standard"
        )

        # Should have conditional logic, not quota
        assert "IF issues_found" in result.prompt or "EVALUATION PROTOCOL" in result.prompt
        # Should NOT have "MUST find at least N"
        assert "MUST find at least" not in result.prompt


class TestAgentRegistry:
    """Test agent type registry."""

    def test_list_all_agents(self):
        """Test listing all agents."""
        agents = list_agents()
        assert len(agents) > 40  # We have 40+ agents

    def test_list_by_tier(self):
        """Test filtering by tier."""
        implementation_agents = list_agents(tier="implementation")
        judgment_agents = list_agents(tier="judgment")

        assert all(a["tier"] == "implementation" for a in implementation_agents)
        assert all(a["tier"] == "judgment" for a in judgment_agents)

    def test_list_by_domain(self):
        """Test filtering by domain."""
        backend_agents = list_agents(domain="backend")

        assert all(a["domain"] == "backend" for a in backend_agents)
        assert len(backend_agents) > 0

    def test_backend_architect_exists(self):
        """Test that common agent types exist."""
        agents = list_agents()
        agent_types = [a["type"] for a in agents]

        assert "backend-architect" in agent_types
        assert "security-auditor" in agent_types
        assert "cost-analyst" in agent_types
        assert "frontend-developer" in agent_types

    def test_new_agent_types_exist(self):
        """Test that newly added agent types are registered."""
        agents = list_agents()
        agent_types = [a["type"] for a in agents]

        # Verify new system agents
        assert "agent-expert" in agent_types
        assert "context-manager" in agent_types

        # Verify new implementation agents
        assert "documentation-expert" in agent_types
        assert "nextjs-architecture-expert" in agent_types
        assert "react-performance-optimizer" in agent_types
        assert "architecture-modernizer" in agent_types
        assert "code-simplifier" in agent_types
        assert "url-context-validator" in agent_types
        assert "url-link-extractor" in agent_types

        # Verify feature-dev sub-agents
        assert "feature-dev-code-reviewer" in agent_types
        assert "feature-dev-code-explorer" in agent_types
        assert "feature-dev-code-architect" in agent_types


class TestComplexityScoring:
    """Test task complexity scoring."""

    def test_empty_task_score_zero(self):
        """Test empty task scores zero."""
        score = score_task_complexity("")
        assert score == 0

    def test_simple_task_low_score(self):
        """Test simple task has low score."""
        score = score_task_complexity("Fix a bug")
        assert score < 20

    def test_complex_task_high_score(self):
        """Test complex task has high score."""
        task = """
        Design a HIPAA compliant telemedicine platform with real-time video consultations,
        secure messaging, payment processing, and integration with electronic health records.
        Must meet SOC2 compliance requirements and support 10,000 concurrent users.
        """
        score = score_task_complexity(task)
        assert score > 50

    def test_technical_keywords_increase_score(self):
        """Test that technical keywords increase score."""
        simple = "Build a website"
        technical = "Design a scalable microservices architecture with API gateway"
        technical2 = "Implement distributed database with event sourcing and CQRS"

        assert score_task_complexity(simple) < score_task_complexity(technical)
        assert score_task_complexity(technical) < score_task_complexity(technical2)


class TestPromptValidation:
    """Test prompt validation."""

    def test_validate_good_prompt_passes(self):
        """Test that a good prompt passes validation."""
        prompt = """
        You are a security-auditor.

        TASK: Review this code for vulnerabilities.

        EVALUATION PROTOCOL:
        IF issues_found > 0:
            Report all issues with severity and remediation
        ELSE:
            State 'No issues found. Verified: [checklist]'
        """

        result = validate_prompt(prompt, "security-auditor")
        assert result["valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_missing_anti_sycophancy_fails(self):
        """Test that missing anti-sycophancy for judgment agents fails."""
        prompt = "You are a cost-analyst. Evaluate this proposal."

        result = validate_prompt(prompt, "cost-analyst")
        assert result["valid"] is False
        assert any("anti-sycophancy" in issue.lower() for issue in result["issues"])

    def test_validate_long_prompt_warns(self):
        """Test that overly long prompts trigger warning."""
        # Create a very long prompt
        long_prompt = "You are an agent.\n" + "Some instruction.\n" * 100

        result = validate_prompt(long_prompt, "backend-architect")
        assert result["estimated_tokens"] > 300
        assert any("long" in issue.lower() for issue in result["issues"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
