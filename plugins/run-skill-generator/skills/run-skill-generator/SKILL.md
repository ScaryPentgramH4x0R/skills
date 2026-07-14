---
name: run-skill-generator
description: "Queries the cyber-orchestrator-authority skill registry for the closest matching cybersecurity skill before executing any pentest technique, then runs it. Scaffolds and registers a new skill when no match exists. Use at the start of every pentest phase step before running commands."
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
---

# Run Skill Generator

Enforces a skill-first workflow: look up the registered cybersecurity skill before writing or running any pentest command. When no skill covers the technique, generate one and register it.

## When to Use

- Before running **any** pentest or recon command (nmap, curl, subfinder, sqlmap, nikto, etc.)
- At every phase transition in a structured engagement (Foundation → Enumeration → Exploitation)
- When an operator requests `/run-skill-generator` explicitly
- When you would otherwise write raw bash for a security technique

## When NOT to Use

- For non-security tasks (file editing, git ops, code review)
- When the operator explicitly overrides and says to skip the skill lookup

## Rationalizations to Reject

- **"I already know how to run nmap"** — The skill may contain engagement-specific flags, evasion config, or scope constraints that raw knowledge lacks.
- **"The registry won't have this"** — Query first, assume nothing. 876 skills are registered; many overlap in surprising ways.
- **"The skill lookup adds latency"** — Correct methodology beats fast-but-wrong execution.
- **"The skill SKILL.md path is missing"** — Generate it. That's the generator half of this skill.

---

## Workflow

```
Skill-First Checklist:
- [ ] Step 1: Identify the technique about to be run
- [ ] Step 2: Query the orchestrator registry (top 5 matches)
- [ ] Step 3: If match found → read its SKILL.md, follow guidance
- [ ] Step 4: If no match → generate SKILL.md, register, then execute
- [ ] Step 5: Run commands per skill guidance
- [ ] Step 6: Store findings in phase report
```

---

## Quick Start

### Step 1 — Query the registry

Always run this before a technique:

```bash
cd /home/user/cyber-orchestrator-authority && node --input-type=module <<'JSEOF'
import { SkillsRegistry } from './src/skills/SkillsRegistry.js';
import { BrainInitializer } from './src/brain/BrainInitializer.js';

const brain = new BrainInitializer();
await brain.boot();
const sr = new SkillsRegistry();
await sr.loadRegistry([{ id: 'masriyan/cybersecurity-skill', version: 'v3.0.0' }]);

const query = process.env.SKILL_QUERY || 'subdomain enumeration';
const results = sr.search(query).slice(0, 5);
results.forEach((s, i) => {
  console.log(`[${i+1}] ${s.name}`);
  console.log(`    ${s.description}`);
  console.log(`    path: ${s.path}`);
  console.log('');
});
if (!results.length) console.log('NO MATCH — generate new skill');
JSEOF
```

Set `SKILL_QUERY` to your technique keyword. Example:
```bash
SKILL_QUERY="session fixation java" node --input-type=module ...
```

### Step 2 — Read the matched skill

If a match is found, read its SKILL.md:
```bash
cat /home/user/cyber-orchestrator-authority/cybersecurity-skills/main-skills/<skill-name>/SKILL.md
```

Use the skill's methodology, tool flags, and phase guidance to drive execution.

### Step 3 — If no match: generate a new skill

See [skill-scaffold.md]({baseDir}/references/skill-scaffold.md) for the template.

Run the scaffold script:
```bash
SKILL_NAME="your-technique-name" \
SKILL_DESC="One-line description" \
python3 {baseDir}/scripts/scaffold_skill.py
```

Then register it — see [registration.md]({baseDir}/references/registration.md).

---

## Phase → Skill Mapping

| Phase | Technique | Likely skill keyword |
|---|---|---|
| 1 Foundation | DNS/cert recon | `dns enumeration` `osint reconnaissance` |
| 2 Enumeration | Subdomain brute | `subdomain enumeration subfinder` |
| 2 Enumeration | HTTP headers | `web application headers` |
| 2 Enumeration | Port scan | `network scanning nmap` |
| 3 Specialized | SQL injection | `sql injection exploitation` |
| 3 Specialized | Session testing | `session fixation web` |
| 4 Exploitation | API fuzzing | `api injection vulnerabilities` |
| 4 Exploitation | SSRF | `server side request forgery` |
| 4 Exploitation | Auth bypass | `authentication bypass` |

---

## Advanced Usage

See [skill-scaffold.md]({baseDir}/references/skill-scaffold.md) for full scaffold template and field guidance.

See [registration.md]({baseDir}/references/registration.md) for how to register a generated skill with the orchestrator's index.
