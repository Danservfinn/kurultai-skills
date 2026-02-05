# Kurultai Workflow Examples

This directory contains example workflows demonstrating skill composition patterns for the Kurultai CLI.

## Overview

Workflows in Kurultai are YAML files that define multi-step processes using the skill system. They enable:

- **Sequential execution**: Steps that depend on previous outputs
- **Parallel execution**: Independent steps running simultaneously
- **Variable substitution**: Dynamic values passed at runtime
- **Output chaining**: Using results from one step as input to another
- **Error handling**: Continue on failure or stop on error

## Available Workflows

### 1. Feature Development (`feature-development.yaml`)

A complete feature development pipeline that designs, plans, implements, reviews, and tests a new feature.

**Steps:**
1. **Design** (`horde-brainstorming`): Generate architecture and design decisions
2. **Plan** (`horde-plan`): Create detailed implementation plan
3. **Implement** (`horde-implement`): Build the feature
4. **Review** (`code-reviewer`): Review code quality
5. **Test** (`test-generator`): Generate comprehensive tests

**Usage:**
```bash
kurultai workflow run examples/feature-development.yaml \
  --var feature_name="user-authentication" \
  --var description="Add JWT-based user authentication" \
  --var tech_stack="python"
```

**Key Features:**
- Sequential execution with dependencies
- Output chaining between steps
- Comprehensive artifact generation

---

### 2. Code Review (`code-review.yaml`)

Comprehensive code review with parallel quality checks and aggregated reporting.

**Steps:**
1. **Initial Review** (`code-reviewer`): Baseline code quality assessment
2. **Documentation Check** (`doc-generator`): Verify docs completeness (parallel)
3. **Test Coverage** (`test-generator`): Analyze test coverage (parallel)
4. **Security Scan** (`security-auditor`): Security vulnerability scan (parallel)
5. **Aggregate** (`horde-synthesize`): Combine all results

**Usage:**
```bash
kurultai workflow run examples/code-review.yaml \
  --var target_path="./src" \
  --var depth="thorough" \
  --var language="python"
```

**Key Features:**
- Parallel execution for efficiency
- Multiple quality dimensions
- Unified scoring and reporting

---

### 3. Research Analysis (`research-analysis.yaml`)

Research workflow that extracts insights, analyzes findings, and generates reports.

**Steps:**
1. **Gather** (`horde-learn`): Extract insights from sources
2. **Analyze** (`horde-brainstorming`): Identify patterns and implications
3. **Validate** (`horde-synthesize`): Cross-reference and validate findings
4. **Report** (`doc-generator`): Generate formatted research report
5. **Recommend** (`horde-brainstorming`): Create actionable recommendations

**Usage:**
```bash
kurultai workflow run examples/research-analysis.yaml \
  --var topic="AI Safety in Production" \
  --var sources="papers,blogs,news" \
  --var depth="deep"
```

**Key Features:**
- Context passing between steps
- Multi-perspective analysis
- Structured recommendations

---

## Workflow Structure

A workflow file has the following structure:

```yaml
workflow:
  name: workflow-name
  version: 1.0.0
  description: Description of the workflow

  # Variables that can be overridden at runtime
  variables:
    var_name:
      description: "What this variable is for"
      required: true
      default: "default-value"

  # Steps to execute
  steps:
    - id: step_id
      name: "Human-readable name"
      skill: skill-name
      description: "What this step does"
      inputs:
        param: "{{ variable }}"  # Variable substitution
        context: "{{ steps.other_step.outputs.output_name }}"  # Output chaining
      outputs:
        - output_name
      depends_on:
        - other_step
      parallel_group: group_name  # For parallel execution

  # Final outputs
  outputs:
    summary:
      description: "Description"
      value: "{{ steps.step_id.outputs.output_name }}"

  # Execution configuration
  config:
    continue_on_error: false
    step_timeout: 300
    max_retries: 2
    parallel:
      enabled: true
      max_workers: 4
```

---

## Variable Substitution

Variables are defined in the `variables` section and can be referenced using `{{ variable_name }}`.

### Defining Variables

```yaml
variables:
  feature_name:
    description: "Name of the feature"
    required: true
    default: "new-feature"
  review_depth:
    description: "Review depth"
    default: "thorough"
```

### Using Variables

```yaml
steps:
  - id: review
    skill: code-reviewer
    inputs:
      path: "{{ target_path }}"
      depth: "{{ review_depth }}"
```

### Runtime Override

```bash
kurultai workflow run workflow.yaml \
  --var feature_name="my-feature" \
  --var review_depth="strict"
```

---

## Output Chaining

Outputs from one step can be used as inputs to subsequent steps.

### Step Output Definition

```yaml
steps:
  - id: design
    skill: horde-brainstorming
    outputs:
      - design_document
      - architecture_diagram
```

### Using Step Outputs

```yaml
steps:
  - id: plan
    skill: horde-plan
    inputs:
      design: "{{ steps.design.outputs.design_document }}"
    depends_on:
      - design
```

### Output Aggregation

```yaml
outputs:
  summary:
    value: |
      Design: {{ steps.design.outputs.design_document }}
      Plan: {{ steps.plan.outputs.implementation_plan }}
```

---

## Parallel Execution

Steps can run in parallel when they don't depend on each other.

### Defining Parallel Groups

```yaml
steps:
  - id: check_docs
    skill: doc-generator
    parallel_group: quality_checks

  - id: check_tests
    skill: test-generator
    parallel_group: quality_checks

  - id: check_security
    skill: security-auditor
    parallel_group: quality_checks
```

### Configuration

```yaml
config:
  parallel:
    enabled: true
    max_workers: 4
    groups:
      quality_checks:
        - check_docs
        - check_tests
        - check_security
```

---

## Creating Custom Workflows

### 1. Start with a Template

Copy an existing workflow and modify it:

```bash
cp examples/feature-development.yaml my-workflow.yaml
```

### 2. Define Your Variables

Identify what inputs your workflow needs:

```yaml
variables:
  input_file:
    description: "Path to input file"
    required: true
  output_format:
    description: "Output format"
    default: "json"
```

### 3. Define Your Steps

List the skills you need and their dependencies:

```yaml
steps:
  - id: parse
    name: Parse Input
    skill: parser
    inputs:
      file: "{{ input_file }}"
    outputs:
      - parsed_data

  - id: transform
    name: Transform Data
    skill: transformer
    inputs:
      data: "{{ steps.parse.outputs.parsed_data }}"
    outputs:
      - transformed_data
    depends_on:
      - parse
```

### 4. Validate Your Workflow

```bash
kurultai workflow validate my-workflow.yaml
```

### 5. Run Your Workflow

```bash
kurultai workflow run my-workflow.yaml --var input_file="data.json"
```

---

## CLI Commands

### List Available Workflows

```bash
kurultai workflow list
```

### Validate a Workflow

```bash
kurultai workflow validate <workflow-file>
```

### Run a Workflow

```bash
kurultai workflow run <workflow-file> [options]

Options:
  --var KEY=VALUE    Set workflow variable
  --dry-run          Show what would be executed
  --output FORMAT    Output format (json|yaml|table)
```

---

## Best Practices

1. **Use descriptive step IDs**: Makes debugging and logging clearer
2. **Define defaults**: Provide sensible defaults for optional variables
3. **Document outputs**: Clearly document what each step produces
4. **Handle errors**: Set `continue_on_error: true` when partial results are useful
5. **Use parallel groups**: Group independent steps for faster execution
6. **Chain outputs explicitly**: Always use `depends_on` to clarify dependencies
7. **Set appropriate timeouts**: Adjust `step_timeout` based on expected duration

---

## Example: Simple Custom Workflow

```yaml
workflow:
  name: document-process
  version: 1.0.0
  description: Process and analyze documents

  variables:
    document_path:
      description: "Path to document"
      required: true
    analysis_type:
      description: "Type of analysis"
      default: "summary"

  steps:
    - id: read
      name: Read Document
      skill: doc-reader
      inputs:
        path: "{{ document_path }}"
      outputs:
        - content
        - metadata

    - id: analyze
      name: Analyze Content
      skill: text-analyzer
      inputs:
        content: "{{ steps.read.outputs.content }}"
        type: "{{ analysis_type }}"
      outputs:
        - analysis
      depends_on:
        - read

  outputs:
    result:
      description: "Analysis result"
      value: "{{ steps.analyze.outputs.analysis }}"

  config:
    continue_on_error: false
    step_timeout: 120
```

Run it:

```bash
kurultai workflow run document-process.yaml \
  --var document_path="./doc.txt" \
  --var analysis_type="sentiment"
```

---

## Troubleshooting

### Workflow validation fails

Check the workflow structure:
- All required fields are present
- Variable references use correct syntax: `{{ variable_name }}`
- Step dependencies reference existing step IDs

### Step execution fails

- Check skill is installed: `kurultai list`
- Verify input parameters match skill expectations
- Review step logs for error details

### Output chaining not working

- Ensure `depends_on` is set correctly
- Verify output names match what the skill produces
- Check that the previous step completed successfully

---

## See Also

- `skill.yaml` - Example skill manifest
- Kurultai CLI documentation
- Skill development guide
