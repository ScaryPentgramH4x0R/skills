---
name: orchestrator
description: "Session-wide skill and plugin orchestrator. Discovers all available skills, agents, MCP tools, and plugins loaded in the current session, then routes complex tasks to the best-matching capability. Supports token budget options (--budget aggressive|balanced|minimal) to control per-agent context allocation. Use when a task spans multiple skills, when you want automatic specialist routing, or when managing token efficiency across a long session."
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# Orchestrator

Routes tasks to the best available skill, agent, or MCP tool loaded in the current session. Supports token budget options to control how much context each delegated step consumes.

## When to Use

- A task touches multiple domains (recon + exploitation + reporting, or analysis + fix + review)
- You want automatic routing to the right specialist without knowing which skill covers it
- Token efficiency matters — long sessions where context budget must be managed
- You want to delegate to the best available capability across all loaded plugins

## When NOT to Use

- Simple single-step tasks where you already know the right skill to invoke
- Tasks that require tight back-and-forth with the user mid-execution (orchestration works best for well-specified work)
- When you need to override routing manually — just invoke the skill directly with `/skill-name`

---

## Token Budget Options

Pass a budget flag when invoking to control per-agent context allocation:

| Flag | Alias | Per-agent tokens | Compact at | Best for |
|------|-------|-----------------|------------|----------|
| `--budget aggressive` | `-ba` | 1,000 | 70% | Long sessions, many agents, tight context |
| `--budget balanced` | `-bb` | 2,000 | 80% | Default — most tasks |
| `--budget minimal` | `-bm` | 4,000 | 90% | Short sessions, high-fidelity context needed |

**Examples:**
```
/orchestrator:orchestrator --budget aggressive analyze this codebase for injection sinks
/orchestrator:orchestrator --budget minimal run a full auth security review
/orchestrator:orchestrator route this pentest phase: subdomain enum then port scan then vuln check
```

When no `--budget` flag is given, default is `balanced`.

---

## Step 0: Parse Invocation

Extract budget flag and task description from the invocation:

```
input: /orchestrator:orchestrator [--budget <mode>|-ba|-bb|-bm] <task>
```

Set `TOKEN_BUDGET` to the selected mode (default: `balanced`).  
Set `TASK` to the remaining text after the flag.

---

## Step 1: Discover Session Resources

Enumerate everything available in the current session. Run these probes:

**Skills and plugins:**
```bash
# Project skills
find . .claude ~/.claude -maxdepth 4 -name "SKILL.md" 2>/dev/null \
  | xargs grep -l "^description:" 2>/dev/null \
  | head -40

# Skill descriptions
find . .claude ~/.claude -maxdepth 4 -name "SKILL.md" 2>/dev/null \
  | xargs grep -h "^description:" 2>/dev/null \
  | sed 's/^description: //' | head -40
```

**Available slash commands (skill names from directories):**
```bash
find . .claude ~/.claude -maxdepth 4 -type d -name "SKILL.md" -prune -o \
  -path "*/.claude/skills/*" -type d -print 2>/dev/null | head -20
```

Build a catalog:
```
RESOURCES = {
  skills: [ { name, description, path } ],
  mcps:   [ { name, tools: [] } ],     # from session system-reminder if visible
  agents: [ { name, description } ],   # from .claude/agents/ if present
}
```

---

## Step 2: Decompose the Task

Break `TASK` into subtasks, each mappable to a single resource:

1. Identify distinct phases or steps in the task
2. For each subtask, extract: *domain*, *action verb*, *scope*
3. Mark dependencies (subtask B requires output of A)
4. Identify which subtasks can run in parallel

**Decomposition output:**
```
SUBTASKS = [
  { id: 1, description: "...", domain: "...", depends_on: [] },
  { id: 2, description: "...", domain: "...", depends_on: [1] },
  ...
]
```

---

## Step 3: Match Resources

For each subtask, score every resource:

| Signal | Score |
|--------|-------|
| Keyword exact match in description | +3 |
| Domain match (security/analysis/review) | +2 |
| Partial keyword overlap | +1 |
| Explicit exclusion in "When NOT to Use" | −3 |

Pick the highest-scoring resource per subtask. If score < 1, handle the subtask directly without delegation.

---

## Step 4: Apply Token Budget

Translate `TOKEN_BUDGET` to execution constraints:

**aggressive** (`-ba`):
- Max context per delegated subtask: 1,000 tokens
- Summarize intermediate results before passing to next subtask
- Compact accumulated context after each agent completes
- Skip "nice to have" context (background, history)

**balanced** (`-bb`):
- Max context per delegated subtask: 2,000 tokens
- Pass full output of prior subtask to next
- Compact if session context exceeds 80% of budget

**minimal** (`-bm`):
- Max context per delegated subtask: 4,000 tokens
- Preserve full intermediate outputs
- No forced compaction between steps

---

## Step 5: Execute Plan

Present the plan for approval, then execute:

```
Plan (budget: <mode>):
  [1] <subtask 1 description> → <resource name>
  [2] <subtask 2 description> → <resource name> (depends on 1)
  [3] <subtask 3 description> → run directly (no matching skill)

Token budget: <mode> (<N> tokens/agent)
Proceed? [yes/no/edit]
```

On approval:
1. Execute each subtask in dependency order
2. For skill-routed subtasks: invoke with `/skill-name` or the `Skill` tool
3. Apply token budget constraints between steps (summarize or pass full output per mode)
4. Collect outputs
5. Synthesize a final report

---

## Step 6: Report

Deliver a structured summary:

```
Orchestration complete (budget: <mode>)

Results:
  [1] <subtask> — <resource> — ✓ done / ✗ failed
  [2] <subtask> — <resource> — ✓ done
  ...

Synthesis:
  <combined findings or output>

Token usage:
  Estimated context consumed: ~<N> tokens
  Compaction triggered: yes/no
```

---

## Rationalizations to Reject

- **"I can handle this task directly without routing"** — If multiple domains are involved, routing to specialists reduces errors and context waste.
- **"The balanced budget is fine for everything"** — Long sessions with many agents will exhaust context; use `aggressive` when the session is already deep.
- **"I'll skip Step 1 discovery since I know what's available"** — Discovery runs fast and catches skills loaded via plugins that weren't visible at session start.
- **"The task is too complex to decompose"** — Break it down further. Subtasks should be single-domain actions.
