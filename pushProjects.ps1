# A PowerShell script to automate the process of staging, committing, and
# pushing a single Git project from the current directory.
#
# Prerequisite: You must have Git for Windows and the GitHub CLI (gh)
# installed and authenticated.
#
# This script will check if the current folder is a Git repository.
# If it is, it will automatically stage all files, create a new commit,
# and then push to the remote GitHub repository.

# --- SCRIPT CONFIGURATION ---
$DefaultBranch = "main"

# --- MAIN EXECUTION ---

# Step 1: Check for GitHub CLI and Git installations
Write-Host "Checking for prerequisites: Git and GitHub CLI (gh)..."
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Git for Windows not found. Please install it." -ForegroundColor Red
    pause
    exit 1
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "Error: GitHub CLI not found. Please install it and log in." -ForegroundColor Red
    pause
    exit 1
} else {
    Write-Host "All prerequisites found. Proceeding."
}

# Step 2: Check for GitHub authentication.
Write-Host "Checking GitHub authentication status..."
try {
    gh auth status -s > $null
    Write-Host "Authentication successful." -ForegroundColor Green
}
catch {
    Write-Host "You are not authenticated with GitHub CLI." -ForegroundColor Yellow
    Write-Host "Please authenticate now. A browser window will open."
    gh auth login
}

# Step 3: Check if the current folder is a Git repository.
Write-Host "Checking if the current folder is a Git repository..."
if (-not (Test-Path -Path ".\.git" -PathType Container)) {
    Write-Host "Error: The current folder is not a Git repository. Skipping all actions." -ForegroundColor Red
    Write-Host "Please run 'git init' first if you wish to start a new repository here." -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
} else {
    Write-Host "Git repository found. Proceeding with commit and push." -ForegroundColor Green
}

# Step 4: Check for and create a README.md file if it doesn't exist.
Write-Host "Checking for README.md file..."
$readmePath = ".\README.md"
if (-not (Test-Path -Path $readmePath)) {
    Write-Host "README.md not found. Creating a new one." -ForegroundColor Yellow
    $currentDirName = (Get-Item -Path ".\").Name
    # Create a simple markdown file with the project name as a heading
    Set-Content -Path $readmePath -Value "# $currentDirName" -Force
} else {
    Write-Host "README.md file already exists." -ForegroundColor Green
}

# Step 5: Stage and commit all changes.
Write-Host "Staging all changes and creating a new commit..." -ForegroundColor Cyan
git add .
# Check if there are any changes to commit before proceeding.
$commitMessage = "Automated commit at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: No changes to commit. Proceeding with push." -ForegroundColor Yellow
} else {
    Write-Host "Commit successful." -ForegroundColor Green
}

# Step 6: Check if the remote origin exists.
Write-Host "Checking for remote origin..."
$remoteCheck = git remote -v
if ($remoteCheck -match "origin") {
    Write-Host "Remote origin already exists. Pushing to GitHub..." -ForegroundColor Green
    
    # Step 7: Push to the existing remote.
    git push -u origin $DefaultBranch
} else {
    # Step 8: Get the authenticated user's login name.
    $ghUser = (gh api user --jq .login)
    
    # Get the current folder name to use for the new repository.
    $repoName = (Get-Item -Path ".\").Name
    
    Write-Host "No remote origin found. Creating a new repository '$repoName' and pushing..." -ForegroundColor Yellow
    
    # Step 9: Create a new repository on GitHub.
    gh repo create "$repoName" --public --clone=false
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create repository '$repoName' on GitHub. Please check if a repository with that name already exists." -ForegroundColor Red
        Write-Host ""
        pause
        exit 1
    }

    # Step 10: Link local repository and push.
    git remote add origin "https://github.com/$ghUser/$repoName.git"
    git push -u origin $DefaultBranch
}

Write-Host ""
Write-Host "All actions completed." -ForegroundColor Green
Write-Host ""
pause
