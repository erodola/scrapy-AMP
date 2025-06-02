# Usage:
#  .\scrape.ps1 -FromId 100 -ToId 200
# Or:
#  .\scrape.ps1 -ListFile "missing.txt"

param (
    [int]$FromId,
    [int]$ToId,
    [string]$ListFile
)

if ($ListFile) {
    if (-not (Test-Path $ListFile)) {
        Write-Error "The list file '$ListFile' does not exist."
        exit 1
    }
    $ids = Get-Content $ListFile | Where-Object { $_ -match '^\d+$' } | ForEach-Object { [int]$_ }
}
elseif ($FromId -and $ToId) {
    if ($FromId -gt $ToId) {
        Write-Error "FromId must be less than or equal to ToId."
        exit 1
    }
    $ids = $FromId..$ToId
}
else {
    Write-Error "You must provide either -ListFile or both -FromId and -ToId."
    exit 1
}

$projectPath = "."

# Go through artist IDs
foreach ($id in $ids) {
    Write-Host "Scraping artist ID $id..."
    Set-Location $projectPath
    scrapy crawl artist -a id=$id
    Start-Sleep -Seconds 5
}

Write-Host "Finished scraping all requested artist IDs."
