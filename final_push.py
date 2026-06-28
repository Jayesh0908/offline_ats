"""Final Git push script - writes detailed results to file."""
import subprocess
import os
import sys

# Ensure we're in the right directory
os.chdir(r"c:\Users\user\OneDrive\Desktop\offline-ATS\offline_ats")
OUTPUT = r"c:\Users\user\OneDrive\Desktop\offline-ATS\offline_ats\push_complete.txt"

def run_and_log(cmd, step_name):
    """Run command and return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        result = f"[{step_name}] RC={r.returncode}\n{r.stdout}\n{r.stderr}\n\n"
        open(OUTPUT, "a").write(result)
        return r.returncode
    except Exception as e:
        open(OUTPUT, "a").write(f"[{step_name}] ERROR: {str(e)}\n\n")
        return -1

# Clear file
open(OUTPUT, "w").write(f"Starting push at: {os.getcwd()}\n\n")

# 1. Status
run_and_log("git status", "STATUS")

# 2. Add all files
run_and_log("git add -A", "ADD")

# 3. Commit
run_and_log('git commit -m "Initial commit: Complete Offline ATS application"', "COMMIT")

# 4. Push
run_and_log("git push origin master", "PUSH")

# 5. Final log
run_and_log("git log --oneline -3", "LOG")

# 6. Remote verification
run_and_log("git remote -v", "REMOTE")

open(OUTPUT, "a").write("=== PUSH SCRIPT COMPLETE ===\n")
print(f"Done. Check {OUTPUT}")