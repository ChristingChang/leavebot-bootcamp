"""Verify the teaching contract; no app or external service required."""
from pathlib import Path
import json
import re
import sys

root=Path(__file__).resolve().parents[1]
plan=json.loads((root/'course/02-補充/04-PLAN.json').read_text(encoding='utf-8'))
errors=[]
for c in plan['cards']:
    path=root/c['file']
    if not path.exists():errors.append(f'missing prompt {path}')
    elif f'/{c["skill"]}' not in path.read_text(encoding='utf-8'):errors.append(f'prompt {c["id"]}: missing skill invocation')
    if not (root/f'.claude/skills/{c["skill"]}/SKILL.md').exists():errors.append(f'missing skill {c["skill"]}')
for u in plan['day2']['units']:
    for letter in u['cards']:
        if letter not in {c['id'] for c in plan['cards']}:errors.append(f'unit {u["number"]}: missing card {letter}')
for p in (root/'course').rglob('*.md'):
    # Local links only; placeholders are not links. Checkpoints' external receipts live on their branches.
    for href in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if '://' in href or href.startswith('#'):continue
        target=href.split('#')[0]
        if target and not (p.parent/target).exists():errors.append(f'{p.relative_to(root)}: missing {href}')
# Generic methods should not carry course-specific contracts. Archify is vendored separately.
for name in ['compass','to-spec','to-architecture','to-test-plan','to-tickets','implement','tdd','code-review']:
    text=(root/f'.claude/skills/{name}/SKILL.md').read_text(encoding='utf-8')
    if re.search(r'LeaveBot|I0–I4|course/LEAVEBOT|docs/0[1-6]-',text):errors.append(f'{name}: course-specific contract leaked into generic skill')
if errors:raise SystemExit('\n'.join(errors))
print(f'PASS: course {plan["version"]}, {len(plan["cards"])} cards, generic skills and local links')
