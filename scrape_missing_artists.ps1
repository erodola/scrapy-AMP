# Usage: 
#  .\scrape_missing_artists.ps1 -From 18001 -To 19000
# Or:
#  .\scrape_missing_artists.ps1

param (
    [int]$From,
    [int]$To
)

function Process-Range {
    param ([int]$From, [int]$To)

    $archiveName = "$From-$To.7z"
    $archivePath = Join-Path -Path "archived" -ChildPath $archiveName

    if (-not (Test-Path $archivePath)) {
        Write-Error "Archive file not found: $archivePath"
        return
    }

    if (-not (Get-Command "7z" -ErrorAction SilentlyContinue)) {
        Write-Error "7z.exe is not found in PATH. Please install 7-Zip CLI and add it to your PATH."
        return
    }

    $actual = 7z l $archivePath | ForEach-Object {
        if ($_ -match "^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+D") {
            $fullPath = ($_ -split '\s{2,}')[-1]
            if ($fullPath -like "*\*") {
                $subdir = $fullPath.Split('\')[-1]
                if ($subdir -match '^\d+$') {
                    [int]$subdir
                }
            }
        }
    } | Sort-Object -Unique

    $expected = $From..$To
    $missing = $expected | Where-Object { $_ -notin $actual }

    if ($missing.Count -gt 0) {
        $missing | Out-File -FilePath "missing.txt" -Encoding UTF8
        Write-Host "Missing entries written to missing.txt"

        # Invoke scrape.ps1 on missing.txt and wait for it
        Write-Host "Running scrape.ps1 on missing.txt..."
        & .\scrape.ps1 -ListFile "missing.txt"
    }
    else {
        Write-Host "No missing entries in range $From to $To."
    }
}

# Main logic
if ($PSBoundParameters.ContainsKey('From') -and $PSBoundParameters.ContainsKey('To')) {
    Process-Range -From $From -To $To
}
else {
    for ($start = 1; $start -le 19001; $start += 1000) {
        $end = $start + 999
        Process-Range -From $start -To $end
    }
}
