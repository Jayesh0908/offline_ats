@echo off
echo === GIT STATUS ===
git status
echo.
echo === GIT ADD ===
git add -A
echo.
echo === GIT COMMIT ===
git commit -m "Initial commit: Complete Offline ATS application"
echo.
echo === GIT PUSH ===
git push origin master
echo.
echo === DONE ===
pause