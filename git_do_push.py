import subprocess, sys, os

logfile = r"c:\Users\user\OneDrive\Desktop\offline-ATS\git_push_log.txt"

with open(logfile, "w") as f:
    f.write("=== GIT PUSH START ===\n")
    f.write(f"WD: {os.getcwd()}\n\n")
    
    # Step 1: Status
    r = subprocess.run(["git", "status"], capture_output=True, text=True, shell=True)
    f.write(f"=== STATUS (rc={r.returncode}) ===\n{r.stdout}\n{r.stderr}\n\n")
    
    # Step 2: Add
    r = subprocess.run(["git", "add", "-A"], capture_output=True, text=True, shell=True)
    f.write(f"=== ADD (rc={r.returncode}) ===\n{r.stdout}\n{r.stderr}\n\n")
    
    # Step 3: Status after add
    r = subprocess.run(["git", "status"], capture_output=True, text=True, shell=True)
    f.write(f"=== STATUS AFTER ADD (rc={r.returncode}) ===\n{r.stdout}\n{r.stderr}\n\n")
    
    # Step 4: Commit
    r = subprocess.run(["git", "commit", "-m", "Initial commit: Complete Offline ATS application"], capture_output=True, text=True, shell=True)
    f.write(f"=== COMMIT (rc={r.returncode}) ===\n{r.stdout}\n{r.stderr}\n\n")
    
    # Step 5: Push
    r = subprocess.run(["git", "push", "origin", "master"], capture_output=True, text=True, shell=True, timeout=120)
    f.write(f"=== PUSH (rc={r.returncode}) ===\n{r.stdout}\n{r.stderr}\n\n")
    
    # Step 6: Final log
    r = subprocess.run(["git", "log", "--oneline", "-3"], capture_output=True, text=True, shell=True)
    f.write(f"=== LOG (rc={r.returncode}) ===\n{r.stdout}\n{r.stderr}\n\n")
    
    f.write("=== GIT PUSH END ===\n")

print(f"Done! Check: {logfile}")