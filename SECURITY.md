# Security Policy

## Reporting a vulnerability
Please open a private security advisory on GitHub, or email the maintainer. Do not open a public issue for security problems.

## Principles (see docs/ARCHITECTURE.md)
- Prompt injection is treated as UNSOLVED -> the base contains blast radius (least-privilege, sandboxing, HITL, output validation), it does not rely on filtering.
- Secrets never enter prompts or logs (redaction).
- Dependencies are pinned + checksummed; Dependabot + secret scanning are enabled.
- Agent-run code is treated as hostile (sandboxed).
