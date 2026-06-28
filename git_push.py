import subprocess, sys

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    print(f"[{r.returncode}] $ {cmd}")
    if r.stdout: print(r.stdout[:500])
    if r.stderr: print(r.stderr[:500])
    return r.returncode

# 1. Check status
run("git status")

# 2. Check current branch
run("git branch")

# 3. Check remote
run("git remote -v")

# 4. Add everything
run("git add -A")

# 5. Commit if needed
status = subprocess.run("git status --porcelain", capture_output=True, text=True, shell=True)
if status.stdout.strip():
    print("\nChanges to commit:", status.stdout[:500])
    run('git commit -m "Initial commit: Complete Offline ATS application"')

# 6. Push
run("git push origin HEAD")
</write_to_file>