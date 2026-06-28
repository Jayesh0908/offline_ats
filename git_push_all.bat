@echo off
cd /d "C:\Users\user\OneDrive\Desktop\offline-ATS\offline_ats"
echo === GIT STATUS === > ..\git_result.txt
git status >> ..\git_result.txt 2>&1
echo === GIT ADD === >> ..\git_result.txt 2>&1
git add -A >> ..\git_result.txt 2>&1
echo === GIT COMMIT === >> ..\git_result.txt 2>&1
git commit -m "Initial commit: Complete Offline ATS application" >> ..\git_result.txt 2>&1
echo === GIT PUSH === >> ..\git_result.txt 2>&1
git push origin master >> ..\git_result.txt 2>&1
echo === GIT LOG === >> ..\git_result.txt 2>&1
git log --oneline -3 >> ..\git_result.txt 2>&1
echo === DONE === >> ..\git_result.txt 2>&1
echo Script completed. Check ..\git_result.txt
pause