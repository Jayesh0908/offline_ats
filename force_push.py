"""
Force push all project files to GitLab.
Run this script - it will write all output to push_result.txt
"""
import subprocess
import os
import sys

LOG_FILE = "push_result.txt"

def log(msg=""):
    """Write to log file and print."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

def run(cmd, timeout=60):
    """Run a shell command and log output."""
    log(f"\n{'='*60}")
    log(f"RUNNING: {cmd}")
    log(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.stdout:
            log(f"[STDOUT]\n{result.stdout.strip()}")
        if result.stderr:
            log(f"[STDERR]\n{result.stderr.strip()}")
        
        log(f"[EXIT CODE] {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        log(f"[ERROR] {str(e)}")
        return False

def main():
    # Clear log file
    open(LOG_FILE, "w").close()
    
    log("="*60)
    log("OFFLINE ATS - GIT PUSH TO GITLAB")
    log("="*60)
    log(f"Working directory: {os.getcwd()}")
    log(f"Python version: {sys.version}")
    
    # Step 1: Check git status
    log("\n--- STEP 1: Checking Git Status ---")
    run("git status")
    
    # Step 2: Check remote
    log("\n--- STEP 2: Checking Remote ---")
    run("git remote -v")
    
    # Step 3: Add all files
    log("\n--- STEP 3: Adding All Files ---")
    run("git add -A")
    
    # Step 4: Commit
    log("\n--- STEP 4: Committing ---")
    run('git commit -m "Initial commit: Complete Offline ATS application"')
    
    # Step 5: Push to GitLab
    log("\n--- STEP 5: Pushing to GitLab ---")
    success = run("git push origin master", timeout=120)
    
    # Final status
    log("\n--- FINAL STATUS ---")
    run("git log --oneline -3")
    run("git status")
    
    log("\n" + "="*60)
    if success:
        log("✅ SUCCESS! All files pushed to GitLab!")
        log(f"📁 Remote: https://code.swecha.org/Jayesh2026/offline_ats.git")
    else:
        log("❌ Push failed. Check the output above for errors.")
    log("="*60)
    log(f"\nFull output written to: {LOG_FILE}")

if __name__ == "__main__":
    main()