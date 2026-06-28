"""Script to verify and push all changes to GitLab."""
import subprocess
import sys

def run_cmd(cmd, shell=True):
    """Run a command and print output."""
    print(f"\n=== {cmd} ===")
    result = subprocess.run(
        cmd if shell else cmd.split(),
        shell=shell,
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            print(f"  {line}")
    if result.stderr:
        for line in result.stderr.strip().split('\n'):
            print(f"  [ERR] {line}")
    print(f"  Exit code: {result.returncode}")
    return result

def main():
    print("=" * 60)
    print("OFFLINE ATS - Git Push to GitLab")
    print("=" * 60)
    
    # Step 1: Check status
    run_cmd("git status")
    
    # Step 2: Add all files
    run_cmd("git add -A")
    
    # Step 3: Check what would be committed
    result = run_cmd("git status")
    
    # Step 4: Commit
    result = run_cmd('git commit -m "Initial commit: Complete Offline ATS application"')
    
    # Step 5: Show the commit
    run_cmd("git log --oneline -1")
    
    # Step 6: Check where we push to
    run_cmd("git remote -v")
    
    # Step 7: Push
    print("\n\n" + "=" * 60)
    print("PUSHING TO GITLAB...")
    print("=" * 60)
    result = run_cmd("git push origin master")
    
    # Step 8: Verify
    run_cmd("git log --oneline -1")
    
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("SUCCESS! All changes pushed to GitLab.")
    else:
        print("Push may have failed. Check the output above.")
    print("=" * 60)

if __name__ == "__main__":
    main()