Write-Host "=== VTBC BUILD START ===" -ForegroundColor Cyan

# 1. Ensure repo is clean
$dirty = git status --porcelain
if ($dirty) {
    Write-Host "❌ Working tree not clean. Abort." -ForegroundColor Red
    git status --porcelain
    exit 1
}

# 2. Ensure source matches Git (no truncation / logic drift)
git diff --ignore-cr-at-eol --exit-code -- dev
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Source mismatch. Abort." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Source verified" -ForegroundColor Green

# 3. Record build metadata
git rev-parse HEAD > BUILD_COMMIT.txt
git status --porcelain > BUILD_STATUS.txt

# 4. Inject commit into code
$commit = Get-Content BUILD_COMMIT.txt

(Get-Content dev\main.py) `
  -replace 'EXPECTED_COMMIT = "REPLACED_AT_BUILD"', "EXPECTED_COMMIT = `"$commit`"" |
  Set-Content dev\main.py

# 5. Install locked deps
pip install -r requirements.lock.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Dependency install failed." -ForegroundColor Red
    exit 1
}

# 6. Build exe
python -m PyInstaller dev\main.py --onefile --clean --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed." -ForegroundColor Red
    exit 1
}

# 7. Hash exe
Get-FileHash dist\main.exe -Algorithm SHA256 > main.exe.sha256.txt

# 8. Copy commit into dist
Copy-Item BUILD_COMMIT.txt dist
Write-Host "✅ BUILD COMPLETE" -ForegroundColor Green
