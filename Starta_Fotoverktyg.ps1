# Windows launcher for MediaForge. App data and pip cache stay under the app folder;
# Python packages are shared through the current user's Python installation.
param(
    [switch]$UpdatePackages,
    [switch]$InstallLatestPython,
    [int]$WaitForPid = 0,
    [string]$OpenPath = ''
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
$script = Join-Path $PSScriptRoot 'fotoverktyg.pyw'
$dataDir = Join-Path $PSScriptRoot 'MediaForge_Data'
$settingsDir = Join-Path $dataDir 'Settings'
$logDir = Join-Path $PSScriptRoot 'Logs'
$archiveDir = Join-Path $logDir 'Archive'
$cacheDir = Join-Path $dataDir 'PipCache'
$tempDir = Join-Path $dataDir 'Temp'
$startupLog = Join-Path $logDir 'launcher.log'
$errorLog = Join-Path $logDir 'errors.log'
$pythonPackageCheckFile = Join-Path $settingsDir 'PythonPackagesLastCheck.txt'

foreach ($directory in @($settingsDir, $logDir, $archiveDir, $cacheDir, $tempDir)) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}
if (Test-Path -LiteralPath $startupLog -PathType Leaf) {
    $previousLauncherLog = Get-Item -LiteralPath $startupLog
    $today = (Get-Date).Date
    if ($previousLauncherLog.LastWriteTime.Date -lt $today) {
        $logDate = $previousLauncherLog.LastWriteTime.ToString('yyyy-MM-dd')
        $archivedLog = Join-Path $archiveDir "launcher-$logDate.log"
        if (Test-Path -LiteralPath $archivedLog) {
            $archivedLog = Join-Path $archiveDir "launcher-$logDate-$(Get-Date -Format 'HHmmss').log"
        }
        try { Move-Item -LiteralPath $startupLog -Destination $archivedLog -ErrorAction Stop } catch { }
    }
}
$env:PIP_CACHE_DIR = $cacheDir
$env:TEMP = $tempDir
$env:TMP = $tempDir
Remove-Item Env:PYTHONNOUSERSITE -ErrorAction SilentlyContinue

function Write-StartupLog([string]$text) {
    try { Add-Content -LiteralPath $startupLog -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $text") -Encoding UTF8 } catch { }
}
function Write-ErrorLog([string]$text) {
    try { Add-Content -LiteralPath $errorLog -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | ERROR | $text") -Encoding UTF8 } catch { }
}
function Write-WarningLog([string]$text) {
    try { Add-Content -LiteralPath $errorLog -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | WARNING | $text") -Encoding UTF8 } catch { }
}
function Notice([string]$text, [string]$title = 'MediaForge') {
    [System.Windows.Forms.MessageBox]::Show($text, $title, 'OK', 'Information') | Out-Null
}
function Ask([string]$text, [string]$title = 'MediaForge') {
    return [System.Windows.Forms.MessageBox]::Show($text, $title, 'YesNo', 'Question') -eq 'Yes'
}
function Wait-ForParent([int]$pidToWaitFor) {
    if ($pidToWaitFor -le 0) { return }
    while ($true) {
        try { Get-Process -Id $pidToWaitFor -ErrorAction Stop | Out-Null; Start-Sleep -Milliseconds 400 }
        catch { break }
    }
}
function Get-PythonPackageScheduledTime {
    $now = Get-Date
    $daysSinceMonday = (([int]$now.DayOfWeek + 6) % 7)
    $scheduled = $now.Date.AddDays(-$daysSinceMonday).AddHours(8)
    if ($now -lt $scheduled) { $scheduled = $scheduled.AddDays(-7) }
    return $scheduled
}
function Test-PythonPackageRefreshDue {
    if (-not (Test-Path -LiteralPath $pythonPackageCheckFile -PathType Leaf)) { return $true }
    try {
        $lastText = Get-Content -LiteralPath $pythonPackageCheckFile -Raw -ErrorAction Stop
        $lastCheck = [DateTimeOffset]::Parse($lastText, [Globalization.CultureInfo]::InvariantCulture)
        return $lastCheck.LocalDateTime -lt (Get-PythonPackageScheduledTime)
    } catch { return $true }
}
function Record-PythonPackageRefreshAttempt {
    $now = Get-Date
    $slot = Get-PythonPackageScheduledTime
    if ($now.DayOfWeek -eq [DayOfWeek]::Sunday -or ($now.DayOfWeek -eq [DayOfWeek]::Monday -and $now.TimeOfDay -lt [TimeSpan]::FromHours(8))) {
        $slot = $slot.AddDays(7)
    }
    ([DateTimeOffset]$slot).ToString('o') | Set-Content -LiteralPath $pythonPackageCheckFile -Encoding ASCII
}
function Find-LatestWingetPythonId {
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) { return $null }
    $searchText = (& $winget.Source search --query 'Python.Python.3.' --source winget --accept-source-agreements 2>$null | Out-String)
    $matches = [regex]::Matches($searchText, 'Python\.Python\.(\d+\.\d+)')
    $versions = @{}
    foreach ($match in $matches) {
        $versionText = $match.Groups[1].Value
        try { $versions[$versionText] = [version]$versionText } catch { }
    }
    $latest = $versions.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1
    if ($latest) { return "Python.Python.$($latest.Key)" }
    return $null
}
function Install-LatestPython([hashtable]$ExistingPython = $null) {
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) {
        if ($ExistingPython) {
            throw "Python $($ExistingPython.Version) is already installed, but winget is unavailable. It was left unchanged; no second Python installation was attempted."
        }
        Start-Process 'https://www.python.org/downloads/windows/'
        throw 'No compatible Python is installed and winget is unavailable. The official Python download page was opened; install Python 3.10 or later and run the launcher again.'
    }

    if ($ExistingPython) {
        $packageId = "Python.Python.$($ExistingPython.Version)"
        $listedPackages = & $winget.Source list --id $packageId --exact --accept-source-agreements 2>$null | Out-String
        if ($LASTEXITCODE -ne 0 -or $listedPackages -notmatch [regex]::Escape($packageId)) {
            throw "Python $($ExistingPython.Version) is installed but is not managed by winget. It was left unchanged; no second Python installation was attempted."
        }
        Write-StartupLog "Updating existing Python package $packageId"
        $upgradeArgs = @('upgrade', '--id', $packageId, '--exact', '--accept-package-agreements', '--accept-source-agreements')
        & $winget.Source @upgradeArgs >> $startupLog 2>&1
        if ($LASTEXITCODE -ne 0) { throw "winget could not update existing $packageId (exit code $LASTEXITCODE). No new Python installation was attempted. See $startupLog" }
        return $ExistingPython.Version
    }

    $packageId = Find-LatestWingetPythonId
    if (-not $packageId) { throw 'Could not find the latest stable Python package in winget.' }
    Write-StartupLog "Installing Python package $packageId because no compatible Python is installed"
    $installArgs = @('install', '--id', $packageId, '--exact', '--scope', 'user', '--accept-package-agreements', '--accept-source-agreements')
    & $winget.Source @installArgs >> $startupLog 2>&1
    if ($LASTEXITCODE -ne 0) { throw "winget could not install $packageId (exit code $LASTEXITCODE). See $startupLog" }
    return ($packageId -replace '^Python\.Python\.', '')
}
function Find-BasePython([string]$preferredVersion = '') {
    $candidates = @()
    $py = Get-Command 'py.exe' -ErrorAction SilentlyContinue
    if ($py) {
        if ($preferredVersion) { $candidates += ,@{ File = $py.Source; Args = @("-$preferredVersion") } }
        $candidates += ,@{ File = $py.Source; Args = @('-3') }
    }
    foreach ($name in @('python.exe', 'python3.exe')) {
        $candidate = Get-Command $name -ErrorAction SilentlyContinue
        if ($candidate) { $candidates += ,@{ File = $candidate.Source; Args = @() } }
    }
    $versionCode = 'import sys; print("%d.%d" % sys.version_info[:2]); print(getattr(sys, "_base_executable", sys.executable)); raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'
    foreach ($candidate in $candidates) {
        try {
            $commandArgs = @($candidate.Args) + @('-c', $versionCode)
            $probeOutput = @(& $candidate.File @commandArgs 2>$null)
            if ($LASTEXITCODE -eq 0 -and $probeOutput.Count -ge 2) {
                return @{ File = $probeOutput[-1].ToString().Trim(); Args = @(); Version = $probeOutput[0].ToString().Trim(); Executable = $probeOutput[-1].ToString().Trim() }
            }
        } catch { }
    }
    return $null
}
function Invoke-Python([string]$executable, [string[]]$prefixArgs, [string[]]$arguments) {
    $allArgs = @($prefixArgs) + @($arguments)
    & $executable @allArgs
    return $LASTEXITCODE
}

try {
    if (-not (Test-Path -LiteralPath $script)) { throw 'fotoverktyg.pyw is missing from the application folder.' }
    Write-StartupLog 'Launcher started'
    Wait-ForParent $WaitForPid

    $basePython = Find-BasePython
    if ($InstallLatestPython) {
        if (-not (Ask 'Update the installed Python through winget, or install Python only if no compatible version is present? MediaForge will use the resulting runtime.' 'Python runtime')) {
            Write-StartupLog 'Python runtime update/install cancelled by user'
            exit
        }
        $preferredVersion = Install-LatestPython $basePython
        $basePython = Find-BasePython $preferredVersion
        if (-not $basePython) {
            Notice 'The Python runtime was updated or installed, but this launcher could not detect it yet. Run the launcher again after signing out and back in if needed.' 'Python runtime'
            exit
        }
    } elseif (-not $basePython) {
        if (-not (Ask 'Python 3.10 or later is required. Install the latest stable Python available through winget?' 'Install Python')) {
            Write-StartupLog 'Python installation declined'
            exit
        }
        $preferredVersion = Install-LatestPython $basePython
        $basePython = Find-BasePython $preferredVersion
        if (-not $basePython) {
            Notice 'Python was installed. Run this launcher again; Windows may need a new sign-in to refresh PATH.' 'Python runtime'
            exit
        }
    }

    $probeCode = 'import PyQt6, PIL, pillow_heif, piexif'
    $pipProbeArgs = @($basePython.Args) + @('-m', 'pip', '--version')
    & $basePython.File @pipProbeArgs 2>$null
    if ($LASTEXITCODE -ne 0) {
        $ensurePipArgs = @($basePython.Args) + @('-m', 'ensurepip', '--upgrade', '--user')
        & $basePython.File @ensurePipArgs >> $startupLog 2>&1
        if ($LASTEXITCODE -ne 0) { throw "Python's pip module is unavailable. Install pip for Python $($basePython.Version), then rerun MediaForge. See $startupLog" }
    }

    $probeArgs = @($basePython.Args) + @('-c', $probeCode)
    & $basePython.File @probeArgs 2>$null
    $packagesAvailable = ($LASTEXITCODE -eq 0)
    $refreshDue = $UpdatePackages -or (-not $packagesAvailable) -or (Test-PythonPackageRefreshDue)
    if ($refreshDue) {
        Record-PythonPackageRefreshAttempt
        $pipHelpArgs = @($basePython.Args) + @('-m', 'pip', 'install', '--help')
        $pipHelp = (& $basePython.File @pipHelpArgs 2>$null | Out-String)
        $pipArgs = @($basePython.Args) + @('-m', 'pip', 'install', '--user', '--upgrade')
        if ($pipHelp -match '--break-system-packages') { $pipArgs += '--break-system-packages' }
        $pipArgs += @('PyQt6', 'Pillow', 'pillow-heif', 'piexif')
        if ($UpdatePackages) { Write-StartupLog 'User requested a shared Python package refresh' }
        else { Write-StartupLog 'Weekly shared Python package refresh due (Monday 08:00 local time)' }
        & $basePython.File @pipArgs >> $startupLog 2>&1
        $packageUpdateExitCode = $LASTEXITCODE
        & $basePython.File @probeArgs 2>$null
        $packagesAvailable = ($LASTEXITCODE -eq 0)
        if ($packageUpdateExitCode -ne 0) {
            Write-WarningLog "Shared Python package update failed (exit code $packageUpdateExitCode)"
            if (-not $packagesAvailable) { throw "Python package update failed and required packages are unavailable (exit code $packageUpdateExitCode). See $startupLog" }
            Write-StartupLog 'Continuing with the already installed packages.'
        } elseif (-not $packagesAvailable) {
            throw 'Required Python packages could not be verified after the scheduled update.'
        }
    } else {
        Write-StartupLog 'Skipping shared Python package refresh; the weekly Monday 08:00 local-time window has not arrived.'
    }

    $pythonw = Join-Path (Split-Path -Parent $basePython.Executable) 'pythonw.exe'
    if (-not (Test-Path -LiteralPath $pythonw)) { throw "pythonw.exe is missing next to $($basePython.Executable). Cannot start the GUI without a console." }
    Write-StartupLog "Starting MediaForge using shared Python $($basePython.Version)"
    $appArguments = '"' + $script + '"'
    if (-not [string]::IsNullOrWhiteSpace($OpenPath)) {
        $appArguments += ' "' + $OpenPath + '"'
    }
    Start-Process -FilePath $pythonw -ArgumentList $appArguments -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -ErrorAction Stop
} catch {
    $failure = $_.Exception.Message
    Write-StartupLog "Startup failure: $failure"
    Write-ErrorLog "Startup failure: $failure"
    [System.Windows.Forms.MessageBox]::Show($failure, 'MediaForge - startup error', 'OK', 'Error') | Out-Null
}
