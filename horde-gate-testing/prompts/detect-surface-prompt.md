# Detect Integration Surface Prompt

## Purpose

Analyze code to identify the integration surface of a phase - the public functions, classes, exported constants, and data structures that form the contract between this phase and other parts of the system.

## Task Description

You are a subagent responsible for analyzing implementation code to extract its integration surface. The integration surface represents the public API that other phases or components will depend on.

## Input Parameters

- `{{PHASE_NAME}}`: Name of the phase (e.g., "Phase 1: Setup")
- `{{PHASE_NUMBER}}`: Phase number for reference
- `{{FILE_PATHS}}`: List of file paths to analyze
- `{{LANGUAGE}}`: Programming language (python, typescript, javascript, go, rust, etc.)

## Instructions

1. **Read all files** at `{{FILE_PATHS}}`
2. **Identify public exports** - what is exposed for external use
3. **Extract function signatures** - names, parameters, return types
4. **Extract class definitions** - public methods, properties, constructors
5. **Extract constants and types** - exported values and type definitions
6. **Extract data structures** - interfaces, structs, schemas
7. **Document the integration surface** using the output format below

## What to Look For

### Public Functions

- Exported/top-level functions
- Async functions and their return types
- Function parameters and default values
- Generic type parameters

### Classes and Objects

- Exported classes
- Public methods and properties
- Constructor signatures
- Static members
- Abstract classes and interfaces

### Exported Constants

- Configuration constants
- Enum definitions
- Default values
- Magic numbers/strings that are part of the API

### Data Structures

- Type definitions (TypeScript)
- Interfaces and protocols
- Struct definitions (Go, Rust)
- Schema definitions (Pydantic, Zod, etc.)
- Input/output DTOs

### Module Exports

- Default exports
- Named exports
- Re-exports from other modules
- Barrel files

## Output Format

Provide the integration surface analysis in this JSON structure:

```json
{
  "phase": "{{PHASE_NAME}}",
  "phase_number": {{PHASE_NUMBER}},
  "language": "{{LANGUAGE}}",
  "files_analyzed": [
    "path/to/file1.ts",
    "path/to/file2.ts"
  ],
  "integration_surface": {
    "functions": [
      {
        "name": "functionName",
        "signature": "functionName(param1: Type1, param2?: Type2): ReturnType",
        "file": "path/to/file.ts",
        "line": 42,
        "is_async": true,
        "is_exported": true,
        "description": "Brief description of what this function does"
      }
    ],
    "classes": [
      {
        "name": "ClassName",
        "file": "path/to/file.ts",
        "line": 10,
        "is_exported": true,
        "constructor": {
          "signature": "constructor(config: Config)",
          "parameters": ["config: Config"]
        },
        "methods": [
          {
            "name": "methodName",
            "signature": "methodName(arg: Type): ReturnType",
            "is_async": false,
            "visibility": "public"
          }
        ],
        "properties": [
          {
            "name": "propertyName",
            "type": "PropertyType",
            "visibility": "public",
            "readonly": false
          }
        ]
      }
    ],
    "constants": [
      {
        "name": "CONSTANT_NAME",
        "type": "string",
        "value": "default_value",
        "file": "path/to/file.ts",
        "line": 5,
        "is_exported": true
      }
    ],
    "types": [
      {
        "name": "TypeName",
        "definition": "interface TypeName { field: string }",
        "file": "path/to/file.ts",
        "line": 20,
        "is_exported": true,
        "kind": "interface"
      }
    ],
    "enums": [
      {
        "name": "StatusEnum",
        "values": ["PENDING", "ACTIVE", "COMPLETED"],
        "file": "path/to/file.ts",
        "line": 30,
        "is_exported": true
      }
    ]
  },
  "entry_points": [
    {
      "type": "function",
      "name": "mainExport",
      "description": "Primary entry point for this phase"
    }
  ],
  "dependencies": {
    "internal": [
      "../other-phase/module"
    ],
    "external": [
      "package-name"
    ]
  }
}
```

## Rules

1. **Only include public API** - internal/private members should be excluded or marked
2. **Preserve type information** - include full type signatures where available
3. **Include line numbers** - helps with traceability
4. **Note async functions** - critical for integration testing
5. **Capture defaults** - default parameter values are part of the contract
6. **Be exhaustive** - don't miss any exported symbols

## Example Usage

### Input

```
PHASE_NAME: "Phase 2: Neo4j Connection"
PHASE_NUMBER: 2
FILE_PATHS: ["src/lib/neo4j-client.ts", "src/config/neo4j.ts"]
LANGUAGE: typescript
```

### Files Content

```typescript
// src/lib/neo4j-client.ts
import { Driver, Session } from 'neo4j-driver';

export interface Neo4jConfig {
  uri: string;
  username: string;
  password: string;
  database?: string;
}

export class Neo4jClient {
  private driver: Driver;

  constructor(config: Neo4jConfig) {
    // implementation
  }

  async connect(): Promise<void> {
    // implementation
  }

  async runQuery(cypher: string, params?: Record<string, any>): Promise<any> {
    // implementation
  }

  async close(): Promise<void> {
    // implementation
  }
}

export const DEFAULT_TIMEOUT = 30000;
```

### Output

```json
{
  "phase": "Phase 2: Neo4j Connection",
  "phase_number": 2,
  "language": "typescript",
  "files_analyzed": [
    "src/lib/neo4j-client.ts",
    "src/config/neo4j.ts"
  ],
  "integration_surface": {
    "functions": [],
    "classes": [
      {
        "name": "Neo4jClient",
        "file": "src/lib/neo4j-client.ts",
        "line": 10,
        "is_exported": true,
        "constructor": {
          "signature": "constructor(config: Neo4jConfig)",
          "parameters": ["config: Neo4jConfig"]
        },
        "methods": [
          {
            "name": "connect",
            "signature": "connect(): Promise<void>",
            "is_async": true,
            "visibility": "public"
          },
          {
            "name": "runQuery",
            "signature": "runQuery(cypher: string, params?: Record<string, any>): Promise<any>",
            "is_async": true,
            "visibility": "public"
          },
          {
            "name": "close",
            "signature": "close(): Promise<void>",
            "is_async": true,
            "visibility": "public"
          }
        ],
        "properties": []
      }
    ],
    "constants": [
      {
        "name": "DEFAULT_TIMEOUT",
        "type": "number",
        "value": "30000",
        "file": "src/lib/neo4j-client.ts",
        "line": 32,
        "is_exported": true
      }
    ],
    "types": [
      {
        "name": "Neo4jConfig",
        "definition": "interface Neo4jConfig { uri: string; username: string; password: string; database?: string; }",
        "file": "src/lib/neo4j-client.ts",
        "line": 4,
        "is_exported": true,
        "kind": "interface"
      }
    ],
    "enums": []
  },
  "entry_points": [
    {
      "type": "class",
      "name": "Neo4jClient",
      "description": "Main client for Neo4j database connections"
    }
  ],
  "dependencies": {
    "internal": [],
    "external": [
      "neo4j-driver"
    ]
  }
}
```

Return your integration surface analysis in the specified JSON format.
