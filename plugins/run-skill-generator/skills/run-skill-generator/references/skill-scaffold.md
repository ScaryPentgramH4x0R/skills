# Skill Scaffold Template

Use this when no matching skill exists in the orchestrator registry for a technique.

## Template

```markdown
---
name: <kebab-case-technique-name>
description: "<Third-person. What it does + when to trigger>"
---

# <Human Readable Title>

## When to Use
- <Specific scenario 1>
- <Specific scenario 2>

## When NOT to Use
- <Out-of-scope scenario>
- <Better tool exists scenario>

## Rationalizations to Reject
- **"<Common shortcut>"** — <Why it's wrong>

## Execution

### Prerequisites
- Tool: <tool name + install if needed>
- Access level required: <unauthenticated / authenticated / admin>
- Target type: <web app / network / host / API>

### Commands

#### Step 1 — <Name>
```bash
<exact command with flags>
```
**Success:** <what success output looks like>
**Fail:** <what to do if this fails>

#### Step 2 — <Name>
```bash
<exact command>
```

## Output Analysis
- `<pattern>` → <what it means>
- `<pattern>` → <what it means>

## Next Steps
- If <condition> → proceed to <next technique>
- If <condition> → pivot to <alternative>

## Kill Chain Position
<Where this fits: Recon / Weaponization / Delivery / Exploitation / Post-exploitation>
```

## Field Rules

| Field | Rule |
|---|---|
| `name` | kebab-case, ≤64 chars, gerund form preferred |
| `description` | Third-person, include trigger keywords |
| Commands | Include actual flags, not pseudocode |
| Success/Fail | Describe exact output patterns |
| Kill chain | One of the 5-phase positions |

## Registration After Scaffolding

After creating the SKILL.md, register via:
```bash
python3 {baseDir}/scripts/scaffold_skill.py --register /path/to/SKILL.md
```

Or manually add to `/home/user/cyber-orchestrator-authority/cybersecurity-skills/index.json`.
