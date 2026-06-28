import subprocess, os

# Write log to current directory
log_path = os.path.join(os.getcwd(), "git_log.txt")

with open(log_path, "w") as f:
    f.write("=== GIT PUSH START ===\n")
    f.write(f"WD: {os.getcwd()}\n\n")
    
    # Check git
    r = subprocess.run("git status", shell=True, capture_output=True, text=True)
    f.write(f"STATUS (rc={r.returncode}):\n{r.stdout}\n{r.stderr}\n\n")
    
    # Add
    r = subprocess.run("git add -A", shell=True, capture_output=True, text=True)
    f.write(f"ADD (rc={r.returncode}):\n{r.stdout}\n{r.stderr}\n\n")
    
    # Commit
    r = subprocess.run('git commit -m "Initial commit: Offline ATS"', shell=True, capture_output=True, text=True)
    f.write(f"COMMIT (rc={r.returncode}):\n{r.stdout}\n{r.stderr}\n\n")
    
    # Push
    r = subprocess.run("git push origin master", shell=True, capture_output=True, text=True, timeout=120)
    f.write(f"PUSH (rc={r.returncode}):\n{r.stdout}\n{r.stderr}\n\n")
    
    # Log
    r = subprocess.run("git log --oneline -3", shell=True, capture_output=True, text=True)
    f.write(f"LOG (rc={r.returncode}):\n{r.stdout}\n{r.stderr}\n\n")
    
    f.write("=== DONE ===\n")

print(f"Log written to: {log_path}")
print("File exists:", os.path.exists(log_path))