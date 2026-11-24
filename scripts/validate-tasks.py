"""Validate tasks.json against itself, STATUS.md and git.

Run from anywhere: python scripts/validate-tasks.py
Exit 0 means the tracker is internally truthful. Exit 1 lists what is not.
"""
import json
import re
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parent
data = json.loads((BASE / "tasks.json").read_text(encoding="utf-8"))
status = (BASE / "STATUS.md").read_text(encoding="utf-8")
errors = []

tasks = [t for obj in data["repos"].values() for t in obj["tasks"]]
by_id = {t["id"]: t for t in tasks}
ids = [t["id"] for t in tasks]

if len(ids) != len(set(ids)):
    errors.append("duplicate task ids")

for t in tasks:
    tid, st, log = t["id"], t["status"], t.get("log")
    if st in ("done", "in-progress"):
        folder = "done" if st == "done" else "in-progress"
        if t.get("logDebt"):
            if log:
                errors.append(f"{tid}: logDebt task unexpectedly carries a log")
        elif not log or f"TASKS/{folder}/" not in log:
            errors.append(f"{tid}: {st} without a log in TASKS/{folder}/")
        elif not (BASE / log).exists():
            errors.append(f"{tid}: log file missing: {log}")
        if t.get("verified") and t.get("logDebt"):
            errors.append(f"{tid}: verified true but logDebt set")
        if t.get("logDebt") and not t.get("verified") is False:
            errors.append(f"{tid}: logDebt tasks must be verified false")
    if st == "todo":
        if log:
            errors.append(f"{tid}: todo carries a log")
        if t.get("finished"):
            errors.append(f"{tid}: todo carries a finished date")
    for dep in t.get("dependsOn", []):
        if dep not in by_id:
            errors.append(f"{tid}: unresolved dependency {dep}")

# cycles
visiting, visited = set(), set()

def walk(tid, path):
    if tid in visiting:
        errors.append("cycle: " + " -> ".join(path + [tid]))
        return
    if tid in visited:
        return
    visiting.add(tid)
    for dep in by_id.get(tid, {}).get("dependsOn", []):
        walk(dep, path + [tid])
    visiting.discard(tid)
    visited.add(tid)

for t in tasks:
    walk(t["id"], [])

s = data["summary"]
actual = {
    "total": len(tasks),
    "done": sum(1 for t in tasks if t["status"] == "done"),
    "in_progress": sum(1 for t in tasks if t["status"] == "in-progress"),
    "backlog": sum(1 for t in tasks if t["status"] == "todo"),
}
for k, v in actual.items():
    if s.get(k) != v:
        errors.append(f"summary.{k}={s.get(k)} but entries say {v}")

debts = sorted(t["id"] for t in tasks if t.get("logDebt"))
if s.get("logDebt") != debts:
    errors.append(f"summary.logDebt={s.get('logDebt')} but entries say {debts}")

for repo, obj in data["repos"].items():
    rt = obj["tasks"]
    expected = (
        len(rt),
        sum(1 for t in rt if t["status"] == "done"),
        sum(1 for t in rt if t["status"] == "in-progress"),
        sum(1 for t in rt if t["status"] == "todo"),
    )
    got = s["byRepo"].get(repo, {})
    declared = (got.get("total"), got.get("done"), got.get("in_progress"), got.get("backlog"))
    if expected != declared:
        errors.append(f"byRepo.{repo}: {declared} vs {expected}")

for phase in data["plan"]["phases"]:
    if len(phase["tasks"]) != phase["count"]:
        errors.append(f"phase {phase['id']}: count {phase['count']} vs {len(phase['tasks'])}")
    for tid in phase["tasks"]:
        if tid not in by_id:
            errors.append(f"phase {phase['id']}: unknown {tid}")

for tid in data["plan"]["nextUp"]:
    if by_id.get(tid, {}).get("status") != "todo":
        errors.append(f"nextUp {tid} is not todo")

for line in status.splitlines():
    cells = [c.strip() for c in line.split("|")[1:-1]] if line.startswith("| `") else []
    if len(cells) < 5:
        continue
    repo = cells[0].strip("`")
    if repo not in s.get("byRepo", {}) or not cells[1].isdigit():
        continue
    declared = tuple(int(x) for x in cells[1:5])
    got = s["byRepo"][repo]
    table_expected = (got["total"], got["done"], got["in_progress"], got["backlog"])
    if declared != table_expected:
        errors.append(f"STATUS table {repo}: {declared} vs summary {table_expected}")

m = re.search(r"Counts: \*\*(\d+) total = (\d+) done \+ (\d+) in-progress \+ (\d+) backlog\*\*", status)
if not m:
    errors.append("STATUS counts line missing")
elif tuple(int(x) for x in m.groups()) != (actual["total"], actual["done"], actual["in_progress"], actual["backlog"]):
    errors.append("STATUS counts disagree with entries")

audit = data.get("followUpAudit", {})
entries = audit.get("entries", {})
if audit.get("total") != len(entries):
    errors.append("followUpAudit total != number of entries")
counts = audit.get("counts", {})
for cls in ("filed", "tracked", "named", "historical"):
    n = sum(1 for v in entries.values() if v.get("class") == cls)
    if counts.get(cls) != n:
        errors.append(f"followUpAudit counts.{cls}={counts.get(cls)} vs {n}")
for key, v in entries.items():
    tid, _, idx = key.partition(":")
    t = by_id.get(tid)
    if not t:
        errors.append(f"audit key has no task: {key}")
        continue
    if int(idx) >= len(t.get("follow_ups", [])):
        errors.append(f"audit index out of range: {key}")
    if v.get("class") in ("filed", "tracked") and v.get("task") not in by_id:
        errors.append(f"audit {key} points to unknown task {v.get('task')}")

for repo, hashes in data.get("unpushed", {}).items():
    local = data["repos"].get(repo, {}).get("localRoot")
    if not local:
        errors.append(f"unpushed repo {repo} has no localRoot")
        continue
    p = ROOT / local.rstrip("/\\")
    for h in hashes:
        r = subprocess.run(["git", "-C", str(p), "cat-file", "-e", h + "^{commit}"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0:
            errors.append(f"unpushed {repo}:{h} is not a commit in {p}")

if errors:
    print("FAILED")
    for e in errors[:60]:
        print(" -", e)
    raise SystemExit(1)
print(f"OK: {actual}; {len(data['plan']['phases'])} phases; "
      f"{len(entries)} follow-ups audited; {len(debts)} log-debt tasks; unpushed hashes verified")
