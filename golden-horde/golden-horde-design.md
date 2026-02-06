# golden-horde Skill Design Document

## Vision

**golden-horde** is an advanced agent team orchestration skill that enables truly decentralized, infinitely scalable collaboration between Claude Code agents. Unlike traditional controller-based patterns, golden-horde uses an event-driven mesh architecture where agents self-organize, discover capabilities, and collaborate emergently.

> "The whole is greater than the sum of its parts" - Aristotle

## Core Principles

1. **Decentralization**: No single point of control or failure
2. **Emergence**: Complex behaviors arise from simple agent interactions
3. **Anti-fragility**: The system gets stronger under stress
4. **Infinite Scale**: Support 10 to 10,000 agents seamlessly
5. **Zero Compromise**: Maximum flexibility WITH maximum safety

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GOLDEN HORDE MESH                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│   │   Agent A   │  │   Agent B   │  │   Agent C   │  │   Agent D   │       │
│   │  (Research) │  │   (Code)    │  │  (Analyze)  │  │   (Test)    │       │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│          │                │                │                │              │
│          └────────────────┼────────────────┼────────────────┘              │
│                           │                │                               │
│          ┌────────────────┴────────────────┴────────────────┐              │
│          │                                                   │              │
│          ▼                                                   ▼              │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                     EVENT BUS (Sharded)                          │      │
│   │                                                                  │      │
│   │  Topics:                                                         │      │
│   │  - capability.discovered    - task.proposed                      │      │
│   │  - finding.shared           - help.requested                     │      │
│   │  - consensus.forming        - state.updated                      │      │
│   │  - agent.heartbeat          - swarm.reconfiguring                │      │
│   │                                                                  │      │
│   │  Features:                                                       │      │
│   │  - Automatic sharding by topic prefix                            │      │
│   │  - Event sourcing with persistent log                            │      │
│   │  - Exactly-once delivery guarantees                              │      │
│   │  - Backpressure and flow control                                 │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                     SWARM INTELLIGENCE LAYER                     │      │
│   │                                                                  │      │
│   │  - Self-organizing teams based on capability matching            │      │
│   │  - Dynamic load balancing across agent population                │      │
│   │  - Emergent consensus without central coordinator                │      │
│   │  - Anti-entropy protocols for state reconciliation               │      │
│   │  - Predictive scaling based on task queue depth                  │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                     SAFETY GUARDRAILS                            │      │
│   │                                                                  │      │
│   │  - Message budgets with automatic throttling                     │      │
│   │  - Circuit breakers on all external dependencies                 │      │
│   │  - Automatic agent quarantine for anomalous behavior             │      │
│   │  - Distributed rate limiting                                     │      │
│   │  - Byzantine fault tolerance for critical decisions              │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Innovations

### 1. Event Sourcing with CQRS

All agent interactions are events. The event log is the single source of truth.

```python
class GoldenHordeEvent:
    """Base event for all golden-horde interactions."""

    event_id: UUID           # Globally unique
    timestamp: datetime      # Vector clock + physical time
    agent_id: str           # Sender identity (signed)
    topic: str              # Routing key (hierarchical)
    payload: dict           # Event data (encrypted)
    signature: str          # Cryptographic signature
    vector_clock: dict      # Causal ordering across agents

    # Safety features
    ttl: int                # Time-to-live (prevents stale events)
    priority: int           # 0-9 (0 = critical, 9 = background)
    idempotency_key: str    # Prevents duplicate processing
```

### 2. Capability-Based Agent Discovery

Agents advertise capabilities, not identities. Teams form dynamically based on needed capabilities.

```python
@dataclass
class Capability:
    """Agent capability advertisement."""

    name: str                    # e.g., "python_code_review"
    confidence: float           # 0.0 - 1.0
    specialization: List[str]   # e.g., ["django", "fastapi"]
    current_load: float         # 0.0 - 1.0
    performance_metrics: dict   # Historical accuracy, speed

class AgentDirectory:
    """Decentralized capability discovery."""

    def find_agents(self, required_capabilities: List[str]) -> List[AgentMatch]:
        """Find agents by capability, not name."""
        # Uses gossip protocol for scalability
        # No central registry - each agent maintains partial view
```

### 3. Swarm Consensus (BFT-Resistant)

For decisions requiring consensus, use Byzantine Fault Tolerant protocols.

```python
class SwarmConsensus:
    """Emergent consensus without central coordinator."""

    def propose(self, proposal: dict, quorum_size: int) -> ConsensusResult:
        """
        Agents vote on proposal.
        Requires 2/3 majority (Byzantine fault tolerance).
        Tolerant of up to (n-1)/3 malicious agents.
        """

    def validate_consensus(self, consensus_id: str) -> bool:
        """Verify consensus was reached correctly."""
```

### 4. Anti-Entropy State Reconciliation

When agents disagree on state, anti-entropy protocols resolve conflicts automatically.

```python
class AntiEntropyProtocol:
    """Automatic state reconciliation."""

    def reconcile(self, agent_a_state: CRDT, agent_b_state: CRDT) -> CRDT:
        """
        Merge divergent states using CRDTs.
        No central authority needed.
        Guaranteed to converge.
        """
```

## Risk Mitigation Strategies

### 1. Message Storm Prevention

**Risk**: Runaway feedback loops generating infinite messages.

**Mitigation**:
```python
class StormPrevention:
    """Multi-layered protection against message storms."""

    # Layer 1: Per-agent message budgets
    DAILY_MESSAGE_BUDGET = 10_000
    HOURLY_MESSAGE_BUDGET = 1_000
    MINUTE_MESSAGE_BUDGET = 100

    # Layer 2: Topic-level rate limiting
    TOPIC_RATE_LIMITS = {
        "finding.shared": 50,      # per minute
        "consensus.vote": 20,      # per minute
        "capability.advertise": 10, # per hour
    }

    # Layer 3: Circuit breakers
    CIRCUIT_BREAKER_THRESHOLD = 100  # messages in 10 seconds
    CIRCUIT_BREAKER_TIMEOUT = 60     # seconds

    # Layer 4: Backpressure
    MAX_QUEUE_DEPTH = 1000
    BACKPRESSURE_STRATEGY = "shed_oldest"  # or "block_producer"

    def check_budget(self, agent_id: str, topic: str) -> BudgetStatus:
        """Check if agent can send message."""
```

### 2. Security Architecture

**Risk**: Malicious agents, spoofing, eavesdropping.

**Mitigation**:
```python
class GoldenHordeSecurity:
    """Defense in depth for agent teams."""

    # Authentication: mTLS + JWT
    def authenticate_agent(self, certificate: X509, token: JWT) -> AgentIdentity:
        """Verify agent identity cryptographically."""

    # Authorization: Capability-based access control
    def authorize_action(self, agent: AgentIdentity, action: str, resource: str) -> bool:
        """Check if agent can perform action on resource."""

    # Encryption: End-to-end for sensitive topics
    def encrypt_payload(self, payload: dict, recipient_key: PublicKey) -> EncryptedPayload:
        """Encrypt for specific recipient."""

    # Message integrity: HMAC signatures
    def sign_message(self, message: GoldenHordeEvent, private_key: PrivateKey) -> str:
        """Cryptographically sign message."""

    # Audit: Tamper-proof logging
    def audit_event(self, event: GoldenHordeEvent) -> AuditRecord:
        """Append-only audit log with Merkle tree verification."""
```

### 3. Debugging and Observability

**Risk**: Impossible to debug distributed agent conversations.

**Mitigation**:
```python
class DistributedTracer:
    """Complete visibility into agent interactions."""

    # Every message gets a trace ID
    # Spans track message flow across agents

    def start_trace(self, task_id: str) -> TraceContext:
        """Begin tracing a distributed workflow."""

    def record_span(self, span: Span, agent_id: str, operation: str):
        """Record operation in distributed trace."""

    def visualize_conversation(self, trace_id: str) -> ConversationGraph:
        """Generate visual graph of agent interactions."""

    def replay_conversation(self, trace_id: str, speed: float = 1.0):
        """Replay conversation for debugging."""

class StructuredLogger:
    """All events logged with correlation IDs."""

    # Log aggregation across all agents
    # Real-time log streaming
    # Pattern detection for anomalies
```

### 4. Fault Tolerance

**Risk**: Cascading failures, split-brain, data loss.

**Mitigation**:
```python
class FaultTolerance:
    """Resilience patterns for agent teams."""

    # Circuit breakers on all external calls
    @circuit_breaker(threshold=5, timeout=60)
    async def call_external_service(self, service: str, request: dict):
        """Fail fast if service is unhealthy."""

    # Bulkhead isolation
    def isolate_team(self, team_id: str) -> TeamSandbox:
        """Run team in isolated resource pool."""

    # Automatic retry with exponential backoff
    @retry(max_attempts=3, backoff=exponential)
    async def send_message(self, message: GoldenHordeEvent):
        """Retry failed message delivery."""

    # Checkpoint and recovery
    def create_checkpoint(self, agent_id: str) -> Checkpoint:
        """Snapshot agent state for recovery."""

    def restore_from_checkpoint(self, checkpoint: Checkpoint) -> AgentState:
        """Recover agent from checkpoint."""
```

### 5. Scalability Safeguards

**Risk**: System collapse under high load.

**Mitigation**:
```python
class ScalabilityGovernor:
    """Automatic scaling and load shedding."""

    # Dynamic team sizing
    def optimal_team_size(self, task_complexity: float) -> int:
        """
        Calculate optimal team size based on task.
        Prevents oversized teams that add overhead.
        """
        return min(3 + int(task_complexity * 5), 20)

    # Load balancing
    def balance_load(self, tasks: List[Task], agents: List[Agent]) -> Assignment:
        """Distribute tasks using consistent hashing."""

    # Auto-scaling
    def scale_agents(self, queue_depth: int, target_latency: float):
        """Automatically add/remove agents based on load."""

    # Graceful degradation
    def degrade_gracefully(self, resource_pressure: float):
        """
        When overloaded:
        1. Reduce consensus requirements
        2. Batch smaller tasks
        3. Shed background work
        4. Maintain critical path
        """
```

## Event Topic Hierarchy

```
golden-horde/
├── agent/
│   ├── discovered          # New agent joined
│   ├── capabilities        # Capability advertisement
│   ├── heartbeat           # Health check
│   ├── unavailable         # Agent failure
│   └── quarantined         # Security isolation
├── task/
│   ├── proposed            # Task needs agents
│   ├── assigned            # Task assigned to team
│   ├── started             # Work begun
│   ├── finding             # Intermediate result
│   ├── blocked             # Needs help
│   ├── completed           # Success
│   └── failed              # Failure with reason
├── consensus/
│   ├── proposed            # Proposal for vote
│   ├── voted               # Agent vote
│   ├── reached             # Consensus achieved
│   └── failed              # Could not agree
├── state/
│   ├── updated             # Shared state change
│   ├── conflict            # Divergence detected
│   └── reconciled          # Conflict resolved
├── swarm/
│   ├── forming             # Team assembling
│   ├── reconfiguring       # Dynamic reorganization
│   ├── disbanding          # Team complete
│   └── learning            # Performance feedback
└── system/
    ├── scaling             # Auto-scale event
    ├── alert               # Anomaly detected
    └── maintenance         # Scheduled maintenance
```

## Usage Example

```python
# User invokes golden-horde
Skill("golden-horde", """
Analyze this codebase for security vulnerabilities using a swarm of specialists.

Task: "Security audit of authentication system"

Constraints:
- Minimum 3 agents, maximum 10
- Must reach consensus on critical findings
- Complete within 30 minutes
- Budget: $50
""")

# golden-horde automatically:
# 1. Discovers available security-capable agents
# 2. Forms optimal team based on specializations
# 3. Assigns sub-tasks through event bus
# 4. Agents collaborate peer-to-peer
# 5. Swarm reaches consensus on findings
# 6. Returns synthesized security report
```

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Event bus with sharding
- Basic agent discovery
- Message signing
- Structured logging

### Phase 2: Collaboration (Week 3-4)
- Peer-to-peer messaging
- Capability matching
- Simple consensus (majority vote)
- State reconciliation

### Phase 3: Intelligence (Week 5-6)
- Swarm formation algorithms
- Dynamic load balancing
- Auto-scaling
- Performance optimization

### Phase 4: Hardening (Week 7-8)
- Byzantine fault tolerance
- Advanced security features
- Chaos engineering tests
- Production readiness

## Success Metrics

| Metric | Target |
|--------|--------|
| Agent team formation | < 5 seconds |
| Message latency (p99) | < 100ms |
| Consensus time | < 10 seconds |
| System throughput | 10,000 events/second |
| Fault tolerance | 33% malicious agents |
| Maximum team size | 100 agents |
| Recovery time | < 30 seconds |

## Files to Create

```
.claude/skills/golden-horde/
├── golden-horde-design.md          # This document
├── golden-horde.py                 # Main skill implementation
├── event_bus.py                    # Sharded event bus
├── agent_directory.py              # Capability discovery
├── swarm_consensus.py              # BFT consensus
├── anti_entropy.py                 # State reconciliation
├── security_layer.py               # Authentication/authorization
├── storm_prevention.py             # Message storm protection
├── distributed_tracer.py           # Observability
├── fault_tolerance.py              # Circuit breakers, retries
├── scalability_governor.py         # Auto-scaling
└── README.md                       # User documentation
```

---

**Next**: Proceed to implementation of core event bus infrastructure.
