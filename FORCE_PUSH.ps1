# This script forces a push to a Git repository from a specified local folder.
# Use this script with caution, as it will overwrite the remote branch with your local content.
# It is a useful tool to fix situations where a repository was created on GitHub,
# but the initial commit and files were not successfully pushed.

# --- SCRIPT CONFIGURATION ---
$DefaultBranch = "main"

# --- MAIN EXECUTION ---

# Step 1: Prompt for the repository folder path
#$RepoPath = Read-Host -Prompt "Enter the full path to the project folder to force push"
$RepoPath = (Get-Item -Path ".\").Name
Write-Host "FOLDER '$RepoPath'"
# Step 2: Check if the folder exists
#if (-not (Test-Path $RepoPath -PathType Container)) {
#    Write-Host "Error: The folder '$RepoPath' was not found. Please check the path and try again." -ForegroundColor Red
#    exit 1
#}

# Step 3: Change directory to the specified folder
#Write-Host "Navigating to folder: '$RepoPath'"
#try {
#    Set-Location $RepoPath
#}
#catch {
#    Write-Host "Error: Failed to change to the directory. Please ensure you have permission." -ForegroundColor Red
#    exit 1
#}

# Step 4: Perform a forced push
Write-Host "Forcing a push to the remote repository on branch '$DefaultBranch'..."
try {
    # The --force flag ensures that the push overwrites the remote repository
    # with the local content, resolving empty repository issues.
    git push --force -u origin $DefaultBranch
    
    Write-Host "Force push completed successfully. Check your GitHub repository to see the files." -ForegroundColor Green
}
catch {
    Write-Host "Error: The force push failed. Please ensure you are in a valid Git repository and are authenticated with GitHub CLI." -ForegroundColor Red
    exit 1
}

# End of script
Write-Host "Script finished."
