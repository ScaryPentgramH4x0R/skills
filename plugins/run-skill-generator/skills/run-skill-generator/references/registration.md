# Skill Registration

After generating a new skill, register it with the orchestrator's index so future queries find it.

## Automatic (via scaffold script)

```bash
python3 {baseDir}/scripts/scaffold_skill.py --register /path/to/new-skill/SKILL.md
```

## Manual

Edit `/home/user/cyber-orchestrator-authority/cybersecurity-skills/index.json`:

```json
{
  "total_skills": <increment by 1>,
  "skills": [
    ...existing entries...,
    {
      "name": "your-skill-name",
      "description": "Same as SKILL.md frontmatter description",
      "path": "cybersecurity-skills/main-skills/your-skill-name",
      "domain": "<recon|enumeration|exploitation|post-exploitation|defensive>"
    }
  ]
}
```

Then verify the orchestrator finds it:

```bash
cd /home/user/cyber-orchestrator-authority && SKILL_QUERY="your keyword" node --input-type=module <<'EOF'
import { SkillsRegistry } from './src/skills/SkillsRegistry.js';
import { BrainInitializer } from './src/brain/BrainInitializer.js';
const brain = new BrainInitializer(); await brain.boot();
const sr = new SkillsRegistry();
await sr.loadRegistry([{ id: 'masriyan/cybersecurity-skill', version: 'v3.0.0' }]);
console.log(sr.search(process.env.SKILL_QUERY).slice(0,3));
EOF
```

## Skill Directory Placement

Place the new skill at:
```
/home/user/cyber-orchestrator-authority/cybersecurity-skills/main-skills/<skill-name>/
├── SKILL.md
└── scripts/
    └── agent.py   (optional)
```
