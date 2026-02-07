"""
Pattern protocol injection for golden-horde patterns.

Provides protocol instructions for different golden-horde coordination patterns.
"""

from typing import Optional


PATTERN_PROTOCOLS = {
    "review-loop": """
REVIEW LOOP PROTOCOL:
- You are participating in an iterative review cycle
- Review artifacts thoroughly and identify specific issues
- Provide feedback with actionable, specific guidance
- Use SendMessage to send feedback with clear issue tags
- Continue until satisfactory or max rounds reached
- Output format: findings with severity and remediation
""",

    "adversarial-debate": """
ADVERSARIAL DEBATE PROTOCOL:
- You are advocating for a specific position in a structured debate
- Make the strongest possible case for your assigned position
- Address opponent's rebuttals directly with evidence
- Challenge assumptions and provide counter-arguments
- A judge will evaluate arguments and rule on contested points
- Output format: position statement with supporting arguments
""",

    "assembly-line": """
ASSEMBLY LINE PROTOCOL:
- You are a stage in a multi-stage processing pipeline
- Your output becomes input for the next stage
- Send completed work forward via SendMessage
- If input is inadequate, specify requirements and send back
- Maintain clear handoff documentation
- Output format: processed artifact with handoff notes
""",

    "consensus-deliberation": """
CONSENSUS DELIBERATION PROTOCOL:
- Provide independent analysis first (don't read others' work)
- Then challenge other experts' findings constructively
- Work toward genuine consensus (not just compromise)
- Converge on recommendations with shared reasoning
- Document any remaining disagreements with rationale
- Output format: consensus report with dissenting views noted
""",

    "watchdog": """
WATCHDOG PROTOCOL:
- Monitor implementers at designated checkpoints
- Identify constraint violations and quality issues in real-time
- Send corrections immediately via SendMessage
- Severity levels: CRITICAL (must fix) | HIGH (should fix) | MEDIUM | LOW
- Track violation patterns and systemic issues
- Output format: violation report with severity and required actions
""",

    "contract-first": """
CONTRACT-FIRST NEGOTIATION PROTOCOL:
- Agree on shared contract before implementation
- Propose contract structure (API, schema, protocol)
- Review counter-proposals and negotiate terms
- Converge on agreed contract with version
- Output format: contract document with version and acceptance status
""",

    "expertise-routing": """
EXPERTISE ROUTING PROTOCOL:
- You are a generalist working on a task
- Route sub-problems to specialist agents via consultation
- Wait for specialist input before continuing
- Integrate specialist recommendations into your work
- Output format: main deliverable with specialist contributions attributed
""",

    "swarm-discovery": """
SWARM DISCOVERY PROTOCOL:
- Explore unknown problem space systematically
- Spawn specialists as sub-problems are discovered
- Aggregate findings from all scouts
- Synthesize into comprehensive map of the space
- Output format: discovery report with findings and recommendations
""",

    "nested-swarm": """
NESTED SWARM PROTOCOL:
- You lead a team that may spawn sub-swarms
- For parallelizable sub-tasks, dispatch multiple agents simultaneously
- Collect and synthesize sub-agent results
- Make final decisions based on aggregated input
- Output format: synthesis with attributed contributions
""",
}


def inject_pattern_protocol(
    prompt: str,
    pattern: str,
    agent_role: Optional[str] = None
) -> str:
    """
    Inject pattern protocol into prompt.

    Args:
        prompt: Base prompt
        pattern: Pattern name (e.g., "review-loop")
        agent_role: Optional role name for customization

    Returns:
        Prompt with protocol injected
    """
    protocol = PATTERN_PROTOCOLS.get(pattern)
    if not protocol:
        return prompt

    # Customize protocol for agent role if specified
    if agent_role:
        # Add role-specific framing
        role_framing = f"\nAs the {agent_role} in this pattern:\n"
        protocol = role_framing + protocol

    return prompt + "\n\n" + protocol.strip()


def list_patterns() -> list:
    """List available pattern protocols."""
    return list(PATTERN_PROTOCOLS.keys())


def get_protocol(pattern: str) -> Optional[str]:
    """Get protocol text for a pattern."""
    return PATTERN_PROTOCOLS.get(pattern)
