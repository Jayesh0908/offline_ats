"""
Complete Git push script for Offline ATS.
Saves all output to a file for verification.
"""
import subprocess, os, sys

# Working directory
WD = r"c:\Users\user\OneDrive\Desktop\offline-ATS\offline_ats"
OUT = os.path.join(WD, "git_complete_log.txt")

os.chdir(WD)

def run(cmd, timeout=120):
    """Run command and return (rc, stdout, stderr)."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)

def log(step, rc, stdout, stderr):
    """Write step results to log file."""
    with open(OUT, "a") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"STEP: {step}\n")
        f.write(f"RETURN CODE: {rc}\n")
        if stdout: f.write(f"STDOUT:\n{stdout}\n")
        if stderr: f.write(f"STDERR:\n{stderr}\n")
        f.write(f"{'='*60}\n")

# Clear log
with open(OUT, "w") as f:
    f.write("GIT PUSH LOG\n")
    f.write(f"Directory: {WD}\n")
    f.write(f"Time: started\n\n")

# Step 1: Check git status
rc, out, err = run("git status")
log("STATUS", rc, out, err)

# Step 2: Add all files
rc, out, err = run("git add -A")
log("ADD ALL", rc, out, err)

# Step 3: Check status after add
rc, out, err = run("git status")
log("STATUS AFTER ADD", rc, out, err)

# Step 4: Commit
rc, out, err = run('git commit -m "Initial commit: Complete Offline ATS application"')
log("COMMIT", rc, out, err)

# Step 5: Push to GitLab
rc, out, err = run("git push origin master")
log("PUSH", rc, out, err)

# Step 6: Verify
rc, out, err = run("git log --oneline -3")
log("LOG", rc, out, err)

# Step 7: Check remote
rc, out, err = run("git remote -v")
log("REMOTE", rc, out, err)

with open(OUT, "a") as f:
    f.write("\n=== GIT PUSH COMPLETE ===\n")

print(f"Done! Check: {OUT}")