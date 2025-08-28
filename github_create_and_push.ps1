# A PowerShell script to automate the process of creating a new GitHub repository
# and pushing the current folder's contents to it on Windows.
#
# Prerequisite: You must have Git for Windows and the GitHub CLI (gh) installed.
# You can get the GitHub CLI from: https://cli.github.com/

# --- SCRIPT CONFIGURATION ---
$DefaultBranch = "main"
$GitIgnoreFile = ".gitignore"
$VenvFolder = ".venv"

# --- MAIN EXECUTION ---

# Step 1: Check for GitHub CLI and Git installations
Write-Host "Checking for prerequisites: Git and GitHub CLI (gh)..."
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git for Windows not found. Please install it first." -ForegroundColor Red
    exit 1
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "GitHub CLI not found. Please install it from https://cli.github.com/ and then re-run this script." -ForegroundColor Red
    exit 1
} else {
    Write-Host "All prerequisites found. Proceeding."
}

# Step 2: Check for GitHub authentication
Write-Host "Checking GitHub authentication status..."
try {
    # This command checks if the user is logged in
    gh auth status
}
catch {
    Write-Host "You are not authenticated with GitHub CLI." -ForegroundColor Yellow
    Write-Host "Please authenticate now. A browser window will open."
    Write-Host "Follow the on-screen instructions to log in."
    
    # This command performs the login and stores credentials
    gh auth login
}

# --- USER INPUT ---

# Use the current folder's name as the repository name
$CurrentDir = (Get-Item -Path ".\").Name
$NewRepoName = Read-Host -Prompt "The suggested repository name is '$CurrentDir'. Press Enter to accept or type a new name."

# If the user enters a new name, use it. Otherwise, use the default.
if ([string]::IsNullOrWhiteSpace($NewRepoName)) {
    $NewRepoName = $CurrentDir
    Write-Host "Using suggested repository name: '$NewRepoName'"
} else {
    Write-Host "Using custom repository name: '$NewRepoName'"
}

# --- GIT & GITHUB CLI COMMANDS ---

# Step 3: Handle .gitignore and initialize the local Git repository
Write-Host "Checking for a .gitignore file..."

# Check if a .gitignore file already exists
if (-not (Test-Path $GitIgnoreFile)) {
    Write-Host "No .gitignore file found. Creating one and adding common exclusions..."
    
    # Create the file and add the virtual environment folder to it
    Set-Content -Path $GitIgnoreFile -Value "$VenvFolder/" -Force
    Write-Host "Added '$VenvFolder/' to .gitignore to prevent committing large files." -ForegroundColor Green
} else {
    Write-Host ".gitignore file already exists."
    # You could add logic here to check if the .venv is already ignored.
}

# Initialize the local Git repository and create the first commit
Write-Host "Initializing local Git repository..."
try {
    # Initialize a new Git repository in the current directory
    git init
    
    # Stage all files in the current directory for the initial commit
    git add .
    
    # Create the first commit with a message
    git commit -m "Initial commit for new project"
    
    Write-Host "Local repository initialized and first commit created." -ForegroundColor Green
}
catch {
    Write-Host "Error: Failed to initialize the local Git repository or create the initial commit." -ForegroundColor Red
    Write-Host "Please ensure you are in the correct project folder and try again." -ForegroundColor Red
    exit 1
}

# Step 4: Create the new repository on GitHub
Write-Host "Creating a new GitHub repository '$NewRepoName'..."
try {
    # Create the new repository on GitHub without trying to push yet
    # The --public flag makes the repository public. Use --private for a private repo.
    # The --clone=false flag prevents gh from trying to clone the new repo locally
    gh repo create "$NewRepoName" --public --clone=false
    
    Write-Host "Repository '$NewRepoName' created on GitHub." -ForegroundColor Green
}
catch {
    Write-Host "Error: Failed to create the GitHub repository." -ForegroundColor Red
    Write-Host "This can happen if a repository with that name already exists." -ForegroundColor Red
    exit 1
}

# Step 5: Link the local repository to the new GitHub repository and push
Write-Host "Linking local repository and pushing to GitHub..."
try {
    # Get the authenticated user's login name from the gh API
    $ghUser = gh api user --jq .login
    
    # Add the newly created GitHub repository as the remote origin
    git remote add origin "https://github.com/$ghUser/$NewRepoName.git"
    
    # Push the local 'main' branch to the remote 'origin'
    git push -u origin $DefaultBranch
    
    Write-Host "Project successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Your new repository is at: https://github.com/$ghUser/$NewRepoName"
}
catch {
    Write-Host "Error: Failed to push to the GitHub repository." -ForegroundColor Red
    Write-Host "Please check the error message above for details." -ForegroundColor Red
    exit 1
}

# End of script
Write-Host "Script finished."
