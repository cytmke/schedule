# Update_Schedule.ps1 - Enhanced version
param()

# Get the directory where this script is located
$scriptDir = $PSScriptRoot
Write-Host "Script directory: $scriptDir"

# The parent directory (where update_schedules.py should be located)
$parentDir = Split-Path -Path $scriptDir -Parent
Write-Host "Parent directory: $parentDir"

# Check if update_schedules.py exists
$pythonScript = Join-Path $parentDir "update_schedules.py"
if (-not (Test-Path $pythonScript)) {
    Write-Error "ERROR: update_schedules.py not found at: $pythonScript"
    Write-Host "Please ensure update_schedules.py exists in the parent directory."
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Call_Schedule directory exists
$callScheduleDir = Join-Path $parentDir "Call_Schedule"
if (-not (Test-Path $callScheduleDir)) {
    Write-Error "ERROR: Call_Schedule directory not found at: $callScheduleDir"
    Write-Host "Please ensure the Call_Schedule folder exists."
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if CallSchedule.txt exists
$scheduleFile = Join-Path $callScheduleDir "CallSchedule.txt"
if (-not (Test-Path $scheduleFile)) {
    Write-Error "ERROR: CallSchedule.txt not found at: $scheduleFile"
    Write-Host "Please ensure CallSchedule.txt exists in the Call_Schedule folder."
    Read-Host "Press Enter to exit"
    exit 1
}

# All checks passed
Write-Host "✓ All required files found:" -ForegroundColor Green
Write-Host "  - update_schedules.py: Found" -ForegroundColor Green
Write-Host "  - CallSchedule.txt: Found" -ForegroundColor Green
Write-Host ""

# Change to the parent directory and run the Python script
Set-Location $parentDir
Write-Host "Running update_schedules.py..." -ForegroundColor Yellow

try {
    # Run the Python script
    python update_schedules.py
    
    # Check exit code
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ update_schedules.py completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "✗ update_schedules.py exited with error code: $LASTEXITCODE" -ForegroundColor Red
    }
}
catch {
    Write-Error "Error running update_schedules.py: $_"
}

Write-Host ""
Read-Host "Press Enter to exit"