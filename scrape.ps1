# Usage:
#  .\scrape.ps1 -From 100 -To 200
# Or:
#  .\scrape.ps1 -ListFile "missing.txt"

param (
    [int]$From,
    [int]$To,
    [string]$ListFile
)

if ($ListFile) {
    if (-not (Test-Path $ListFile)) {
        Write-Error "The list file '$ListFile' does not exist."
        exit 1
    }
    $ids = Get-Content $ListFile | Where-Object { $_ -match '^\d+$' } | ForEach-Object { [int]$_ }
}
elseif ($From -and $To) {
    if ($From -gt $To) {
        Write-Error "From must be less than or equal to To."
        exit 1
    }
    $ids = $From..$To
}
else {
    Write-Error "You must provide either -ListFile or both -From and -To."
    exit 1
}

$projectPath = "."

# Go through artist IDs
foreach ($id in $ids) {
    Write-Host "Scraping artist ID $id..."
    Set-Location $projectPath
    scrapy crawl artist -a id=$id
    Start-Sleep -Seconds 4
}

Write-Host "Finished scraping all requested artist IDs."
