"""
Simplified Git push script.
Run this and it will:
1. Add all files to git
2. Commit them
3. Push to GitLab
4. Save results to C:\temp\git_result.txt
"""
import subprocess, os, sys, tempfile

OUT = r"c:\Users\user\OneDrive\Desktop\offline-ATS\offline_ats\git_final_result.txt"

os.chdir(r"c:\Users\user\OneDrive\Desktop\offline-ATS\offline_ats")

with open(OUT, "w") as f:
    f.write("=== GIT PUSH OPERATION ===\n")
    f.write(f"Time: started\n")
    f.write(f"Directory: {os.getcwd()}\n\n")

def run_cmd(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        with open(OUT, "a") as f:
            f.write(f"$ {cmd}\n")
            f.write(f"Return code: {r.returncode}\n")
            if r.stdout: f.write(f"Output:\n{r.stdout}\n")
            if r.stderr: f.write(f"Errors:\n{r.stderr}\n")
            f.write("---\n\n")
        return r.returncode
    except Exception as e:
        with open(OUT, "a") as f:
            f.write(f"$ {cmd}\n")
            f.write(f"Exception: {str(e)}\n---\n\n")
        return -1

# Step 1: Check status
run_cmd("git status")

# Step 2: Add all files
run_cmd("git add -A")

# Step 3: Check what's staged
run_cmd("git status")

# Step 4: Commit
run_cmd('git commit -m "Initial commit: Complete Offline ATS application"')

# Step 5: Push to GitLab
run_cmd("git push origin master")

# Step 6: Show last commit
run_cmd("git log --oneline -3")

with open(OUT, "a") as f:
    f.write("=== GIT PUSH COMPLETED ===\n")

print(f"Complete! Results written to: {OUT}")