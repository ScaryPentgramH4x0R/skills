#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Scaffold a new cybersecurity skill and optionally register it with the orchestrator index.

Usage:
    python3 scaffold_skill.py --name session-fixation-java --desc "Tests Java web apps for JSESSIONID-in-URL session fixation" --domain exploitation
    python3 scaffold_skill.py --register /path/to/SKILL.md
"""

import argparse
import json
import re
import sys
from pathlib import Path

ORCHESTRATOR_ROOT = Path(__file__).resolve().parents[6] / "cyber-orchestrator-authority"
SKILLS_DIR = ORCHESTRATOR_ROOT / "cybersecurity-skills" / "main-skills"
INDEX_FILE = ORCHESTRATOR_ROOT / "cybersecurity-skills" / "index.json"

SKILL_TEMPLATE = """\
---
name: {name}
description: "{desc}"
---

# {title}

## When to Use
- <Specific scenario>

## When NOT to Use
- <Out-of-scope scenario>

## Rationalizations to Reject
- **"<Common shortcut>"** — <Why it's wrong>

## Execution

### Prerequisites
- Tool: <tool>
- Access level: <unauthenticated / authenticated / admin>

### Commands

#### Step 1 — Detect
```bash
# <detection command>
```
**Success:** <output pattern>
**Fail:** <pivot>

#### Step 2 — Exploit
```bash
# <exploitation command>
```

## Output Analysis
- `<pattern>` → <meaning>

## Next Steps
- If vulnerable → <next step>
- If not vulnerable → <alternative>

## Kill Chain Position
{domain}
"""


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9-]", "-", text.lower()).strip("-")


def scaffold(name: str, desc: str, domain: str) -> Path:
    skill_dir = SKILLS_DIR / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    title = name.replace("-", " ").title()
    skill_md.write_text(SKILL_TEMPLATE.format(name=name, desc=desc, title=title, domain=domain))
    print(f"✓ Scaffolded: {skill_md}")
    return skill_md


def register(skill_md_path: Path) -> None:
    if not INDEX_FILE.exists():
        print(f"ERROR: index not found at {INDEX_FILE}", file=sys.stderr)
        sys.exit(1)

    # Parse frontmatter
    content = skill_md_path.read_text()
    name_match = re.search(r"^name:\s*(.+)$", content, re.M)
    desc_match = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', content, re.M)

    if not name_match or not desc_match:
        print("ERROR: could not parse name/description from frontmatter", file=sys.stderr)
        sys.exit(1)

    name = name_match.group(1).strip()
    desc = desc_match.group(1).strip().strip('"\'')

    index = json.loads(INDEX_FILE.read_text())
    existing = {s["name"] for s in index["skills"]}

    if name in existing:
        print(f"⚠  Already registered: {name}")
        return

    index["skills"].append({
        "name": name,
        "description": desc,
        "path": f"cybersecurity-skills/main-skills/{name}",
        "domain": "custom"
    })
    index["total_skills"] = len(index["skills"])
    INDEX_FILE.write_text(json.dumps(index, indent=2))
    print(f"✓ Registered '{name}' — total skills: {index['total_skills']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold and register cybersecurity skills")
    sub = parser.add_subparsers(dest="cmd")

    new_p = sub.add_parser("new", help="Scaffold a new skill")
    new_p.add_argument("--name", required=True, help="Skill name (kebab-case)")
    new_p.add_argument("--desc", required=True, help="One-line description")
    new_p.add_argument("--domain", default="exploitation", help="Kill chain domain")
    new_p.add_argument("--register", action="store_true", help="Also register after scaffold")

    reg_p = sub.add_parser("register", help="Register an existing SKILL.md")
    reg_p.add_argument("skill_md", help="Path to SKILL.md")

    # Legacy: --register flag at top level
    parser.add_argument("--register", metavar="SKILL_MD", help="Register an existing SKILL.md")
    parser.add_argument("--name")
    parser.add_argument("--desc")
    parser.add_argument("--domain", default="exploitation")

    args = parser.parse_args()

    if args.register and not hasattr(args, "cmd"):
        register(Path(args.register))
        return

    if not args.cmd:
        parser.print_help()
        return

    if args.cmd == "new":
        name = slugify(args.name)
        path = scaffold(name, args.desc, args.domain)
        if args.register:
            register(path)

    elif args.cmd == "register":
        register(Path(args.skill_md))


if __name__ == "__main__":
    main()
