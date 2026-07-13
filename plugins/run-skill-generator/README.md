# run-skill-generator

Enforces a skill-first workflow for penetration testing: query the cyber-orchestrator-authority skill registry before running any technique, and scaffold + register new skills when a gap is found.

## What it does

1. **Query** — searches 876+ registered cybersecurity skills for the closest match to the technique about to be run
2. **Load** — reads the matched skill's `SKILL.md` for methodology, flags, and decision points
3. **Generate** — when no match exists, scaffolds a new `SKILL.md` and registers it in the orchestrator index

## Usage

Invoke before every pentest step:

```bash
# Query registry for a technique
cd /home/user/cyber-orchestrator-authority
SKILL_QUERY="session fixation java" node --input-type=module < query.js

# Scaffold a new skill when no match found
python3 plugins/run-skill-generator/skills/run-skill-generator/scripts/scaffold_skill.py \
  new --name session-fixation-java \
      --desc "Tests Java web apps for JSESSIONID-in-URL session fixation" \
      --domain exploitation \
      --register
```

## Phase Coverage

| Phase | Coverage |
|---|---|
| 1 Foundation | DNS, cert, OSINT |
| 2 Enumeration | Subdomain, API, headers, ports |
| 3 Specialized | SQLi, credentials, cloud |
| 4 Exploitation | API fuzzing, SSRF, auth bypass |
| 5 Advanced | As needed |
