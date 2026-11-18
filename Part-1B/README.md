# Part 1B: AI Code Review Assistant

**Status**: **Under Development**  
**Course**: BITS Pilani WILP (Assignment 1)  

---

## Overview

Part 1B implements an **AI Code Review Assistant** that leverages Large Language Models (LLMs) to perform automated static code analysis, identifying:
- Bugs and edge-case handling defects
- Security vulnerabilities and antipatterns
- Performance bottlenecks
- Maintainability and code smell issues

## Planned Structure

This sub-project maintains dedicated isolation from Part 1A:

```text
Part-1B/
├── .specify/          # Independent Spec Kit project
├── specs/             # Feature specifications & planning artifacts
├── src/               # Code review assistant engine
├── prompts/           # Versioned prompt templates
├── tests/             # Automated test suite
├── evals/             # Evaluation benchmarks
│   └── dataset.json   # Ground-truth evaluation dataset
├── .harness/          # Evaluation harness runner
└── evidence/          # Benchmark results & validation log
```

*Note: Per assignment integrity guidelines, all specifications, prompts, implementation code, evaluation datasets, and evidence will be developed sequentially through the complete Spec-Driven Development (SDD) workflow.*
