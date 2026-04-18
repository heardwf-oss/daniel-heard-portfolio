@echo off
:: ============================================================
:: Daniel Heard Engineering Portfolio - GitHub Pages Deploy
:: Double-click this file in File Explorer to run it
:: ============================================================

cd /d "C:\Users\heard\OneDrive\Documents\daniel-heard-engineering-portfolio"

:: Set up git identity
git config --global user.email "heardwf@gmail.com"
git config --global user.name "Daniel Heard"

:: Initialise repo if needed
if not exist ".git" (
    git init
    git branch -M main
)

:: Add all files
git add .

:: Commit
git commit -m "Portfolio: initial publish"

echo.
echo ============================================================
echo Almost done! Paste your GitHub repo URL below.
echo.
echo  1. Go to: https://github.com/new
echo  2. Name the repo: daniel-heard-portfolio
echo  3. Set it to PUBLIC
echo  4. Do NOT tick README or .gitignore
echo  5. Click Create repository
echo  6. Copy the HTTPS URL (looks like https://github.com/USERNAME/daniel-heard-portfolio.git)
echo  7. Paste it here and press Enter:
echo ============================================================
echo.
set /p REPO_URL=Paste GitHub URL here: 

git remote add origin %REPO_URL%
git push -u origin main

echo.
echo ============================================================
echo Done! Now enable GitHub Pages:
echo  1. Go to your repo on GitHub
echo  2. Click Settings
echo  3. Click Pages (left sidebar)
echo  4. Under Source, select: Deploy from branch
echo  5. Branch: main, Folder: / (root)
echo  6. Click Save
echo  7. Wait 2 minutes, then your live URL will appear there
echo ============================================================
echo.
pause
