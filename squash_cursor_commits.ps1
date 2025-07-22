# PowerShell script to squash all Rav Kohli (formerly Cursor) commits into one per branch and force-push

# Get all local branches
$branches = git branch --format="%(refname:short)"

foreach ($branch in $branches) {
    git checkout $branch

    # Find the oldest commit by Rav Kohli (formerly Cursor)
    $first_commit = git log --reverse --author="Rav Kohli" --format="%H" | Select-Object -First 1

    if ($first_commit) {
        # Find the parent of the first commit
        $parent_commit = git rev-parse "$first_commit^"

        Write-Host "\nBranch: $branch"
        Write-Host "First Rav Kohli commit: $first_commit"
        Write-Host "Parent commit: $parent_commit"
        Write-Host "Starting interactive rebase..."

        # Start interactive rebase from the parent
        git rebase -i $parent_commit

        Write-Host "After completing the rebase in the editor, force-pushing..."
        git push --force origin $branch
    } else {
        Write-Host "No Rav Kohli commits found on $branch. Skipping."
    }
} 