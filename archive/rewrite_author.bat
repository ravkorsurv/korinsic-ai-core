@echo off
REM Batch script to rewrite all Cursor Agent commits to Rav Kohli <rav.kohli@live.co.uk>

REM Change to the repo directory (edit if needed)
cd /d %~dp0

REM Run git-filter-repo with the commit-callback
C:\Users\ravko\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\git-filter-repo.exe --commit-callback rewrite_author.py --force

REM Verify the rewrite
call git log --all --format="%%an <%%ae>" | findstr "Cursor"
call git log --all --format="%%an <%%ae>" | findstr "Rav Kohli"

pause 