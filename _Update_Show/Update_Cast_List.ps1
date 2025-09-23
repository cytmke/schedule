# Update_Cast_List.ps1

# Determine the script folder and base folder (parent of _Update_Show)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$baseDir = Split-Path -Parent $scriptDir  # one level up

# Cast_List folder
$castDir = Join-Path $baseDir "Cast_List"

# Python scripts
$csvPyScript = Join-Path $baseDir "update_cast_from_csv.py"
$pdfPyScript = Join-Path $baseDir "update_cast_from_pdf.py"

# Cast list files
$csvFile = Join-Path $castDir "CastList.csv"
$pdfFile = Join-Path $castDir "CastList.pdf"

# Function to check if CSV is empty (only header or blank lines)
function Is-CsvEmpty($filePath) {
    if (Test-Path $filePath) {
        $lines = Get-Content $filePath | Where-Object { $_.Trim() -ne "" }
        if ($lines.Count -le 1) {
            return $true
        }
    }
    return $false
}

# Check existence of CSV and PDF
$csvExists = (Test-Path $csvFile) -and (-not (Is-CsvEmpty $csvFile))
$pdfExists = Test-Path $pdfFile

if (-not $csvExists -and -not $pdfExists) {
    Write-Host "Error: Neither CastList.csv nor CastList.pdf exist in $castDir."
    Pause
    exit
}

if ((Test-Path $csvFile) -and (Is-CsvEmpty $csvFile) -and (-not $pdfExists)) {
    Write-Host "Error: CastList.csv exists but is empty. Please complete it or add CastList.pdf."
    Pause
    exit
}

# Determine which file to use
$useCsv = $false
$usePdf = $false

if ($csvExists -and $pdfExists) {
    $choice = Read-Host "Both CastList.csv and CastList.pdf exist. Which would you like to use? (csv/pdf)"
    switch ($choice.ToLower()) {
        "csv" { $useCsv = $true }
        "pdf" { $usePdf = $true }
        default {
            Write-Host "Invalid choice. Exiting."
            Pause
            exit
        }
    }
} elseif ($csvExists) {
    Write-Host "Only CastList.csv exists. Using CSV."
    $useCsv = $true
} elseif ($pdfExists) {
    Write-Host "Only CastList.pdf exists. Using PDF."
    $usePdf = $true
}

cd $PSScriptRoot

cd ..

# Run the corresponding Python script
if ($useCsv) {
    Write-Host "Running $csvPyScript ..."
    python "$csvPyScript"
} elseif ($usePdf) {
    Write-Host "Running $pdfPyScript ..."
    python "$pdfPyScript"
}
