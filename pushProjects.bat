@echo off
rem A batch script to iterate through a list of project folders and
rem perform the initial Git push to GitHub.
rem
rem Prerequisite: You must have Git for Windows and the GitHub CLI (gh)
rem installed and authenticated.
rem
rem Important: This script assumes each folder in the list is a separate
rem Git repository with an initial commit already made.

rem --- SCRIPT CONFIGURATION ---
set "defaultBranch=main"

rem Define the list of project folder names you want to process.
rem These names must be the same as the folders you want to push.
rem IMPORTANT: Enclose each project name in double quotes if it contains spaces.
set "projectsToPush="AI AGENT EXAMPLE" "BreakOutImage_ML" "HighVOL_Backtest_streamlit" "intradayDAYSnap" "LINKEDIN_WRITER" "LIVEFEED_STRATEGY" "my-article-writer" "NSE-Stock-Scanner-main" "NSE_DATA_PROCESSING" "OIAnalysis-main" "OI_ANALYSIS" "OutFiles" "RealtimeScanner" "stock-dashboard-master" "super_trader_app" "trade_images_clean" "Trend-Analysis-using-Open-Interest--Rollover-and-FII-DII-Activity-in-Python---Jupyter-Notebook" "tvdatafeed" "UPSTOX_TICKCHART""

rem Set the base directory where your projects are located.
rem This is the parent folder that contains all the project folders.
set "baseDir=D:\py_code_workspace"
 
rem Enable delayed expansion for correct variable handling inside loops.
setlocal enabledelayedexpansion

rem --- MAIN EXECUTION ---
echo.
echo Checking for prerequisites: Git and GitHub CLI (gh)...
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Git for Windows not found. Please install it.
    pause
    exit /b 1
)

where gh >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: GitHub CLI not found. Please install it and log in.
    pause
    exit /b 1
) else (
    echo All prerequisites found. Proceeding.
)

rem Check for GitHub authentication before starting the loop.
echo Checking GitHub authentication status...
gh auth status >nul 2>nul
if %errorlevel% neq 0 (
    echo You are not authenticated with GitHub CLI.
    echo Please log in now. A browser window will open.
    gh auth login
) else (
    echo Authentication successful.
)

echo.
echo Starting the process for each project...
echo.

rem Get the authenticated user's login name.
for /f "delims=" %%a in ('gh api user --jq .login') do set "ghUser=%%a"
echo INSIDE
rem Loop through each project in the list.
rem The double quotes around the project names allow the loop to handle spaces.
for %%f in %projectsToPush% do (
	echo %projectsToPush%
    set "repoName=%%~f"
    set "projectPath=!baseDir!\!repoName!"

    echo --- Processing project: "!repoName!" ---

    rem Step 1: Check if the project folder exists and is a Git repository.
    if not exist "!projectPath!" (
        echo Error: Project folder "!repoName!" not found at "!projectPath!". Skipping.
        echo.
        goto :next_project
    )

    if not exist "!projectPath!\.git" (
        echo Error: "!repoName!" is not a Git repository. Skipping.
        echo.
        goto :next_project
    )

    rem Step 2: Change to the project directory.
    cd /d "!projectPath!"
    if %errorlevel% neq 0 (
        echo Error: Failed to change to directory. Skipping.
        echo.
        goto :next_project
    )

    rem Step 3: Check if the remote origin exists.
    git remote -v | findstr "origin" >nul 2>nul
    if %errorlevel% equ 0 (
        echo Remote origin already exists. Assuming project is already linked.
        echo Pushing to GitHub...
        git push -u origin %defaultBranch%
    ) else (
        echo No remote origin found. Creating repository and pushing...
        
        rem Step 4: Create a new repository on GitHub.
        gh repo create "!repoName!" --public --clone=false
        
        if %errorlevel% neq 0 (
            echo Error: Failed to create repository "!repoName!" on GitHub. Skipping.
            echo.
            goto :next_project
        )

        rem Step 5: Link local repository and push.
        git remote add origin "https://github.com/!ghUser!/!repoName!.git"
        git push -u origin %defaultBranch%
    )

    echo.
    echo Done with project: "!repoName!"
    echo.
    :next_project
)

echo All projects processed.
echo.
pause


