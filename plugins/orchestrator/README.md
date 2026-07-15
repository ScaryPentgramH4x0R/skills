# Orchestrator

Session-wide skill and plugin orchestrator for Claude Code. Discovers all available skills, agents, MCP tools, and plugins loaded in the current session, then routes tasks to the best-matching capability with configurable token budget options.

## What It Does

- **Discovers** everything loaded in the current session: skills, agents, MCP tools, plugins
- **Decomposes** complex multi-domain tasks into subtasks
- **Routes** each subtask to the highest-scoring available resource
- **Controls context** via `--budget aggressive|balanced|minimal` flags

## Install

```bash
claude install trailofbits/skills/orchestrator
```

Or clone and load locally:

```bash
git clone https://github.com/trailofbits/skills
# Add to Claude Code settings: plugins: [{ type: "local", path: "./skills/plugins/orchestrator" }]
```

## Usage

```
/orchestrator:orchestrator [--budget <mode>] <task description>
```

### Token Budget Modes

| Flag | Per-agent tokens | Use when |
|------|-----------------|----------|
| `--budget aggressive` (`-ba`) | 1,000 | Long sessions, many agents |
| `--budget balanced` (`-bb`) | 2,000 | Default |
| `--budget minimal` (`-bm`) | 4,000 | Short sessions, high-fidelity needed |

### Examples

```
/orchestrator:orchestrator enumerate subdomains, scan ports, then check for web vulns
/orchestrator:orchestrator --budget aggressive full security audit of this codebase
/orchestrator:orchestrator --budget minimal review the authentication implementation
```

## How Routing Works

1. **Discovery** — scans `.claude/skills/`, `~/.claude/skills/`, and plugin skill dirs for SKILL.md files
2. **Decomposition** — breaks the task into single-domain subtasks with dependency ordering  
3. **Scoring** — matches each subtask against available resources (+3 exact, +2 domain, +1 partial, −3 exclusion)
4. **Execution** — runs subtasks in dependency order, applying token budget between steps
5. **Synthesis** — collects outputs and delivers a structured report

## Integration with cyber-orchestrator-authority

The token budget modes map directly to the brain's `memory_strategy` settings:

| Budget | Brain strategy | TTL | Access threshold |
|--------|---------------|-----|-----------------|
| aggressive | `aggressive` | 1h | 5 |
| balanced | `balanced` | 24h | 2 |
| minimal | `minimal` | 168h | 1 |
