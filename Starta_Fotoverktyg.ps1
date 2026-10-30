# Windows launcher for MediaForge. App data, its virtual environment, and package cache
# are kept under the application folder. The OS Python runtime is installed separately.
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
$logDir = Join-Path $dataDir 'Logs'
$cacheDir = Join-Path $dataDir 'PipCache'
$tempDir = Join-Path $dataDir 'Temp'
$pythonEnvDir = Join-Path $dataDir 'PythonEnv'
$startupLog = Join-Path $logDir 'launcher.log'
$errorLog = Join-Path $logDir 'errors.log'

foreach ($directory in @($settingsDir, $logDir, $cacheDir, $tempDir, $pythonEnvDir)) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}
$env:PIP_CACHE_DIR = $cacheDir
$env:TEMP = $tempDir
$env:TMP = $tempDir
$env:PYTHONNOUSERSITE = '1'

function Write-StartupLog([string]$text) {
    try { Add-Content -LiteralPath $startupLog -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $text") -Encoding UTF8 } catch { }
}
function Write-ErrorLog([string]$text) {
    try { Add-Content -LiteralPath $errorLog -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | ERROR | $text") -Encoding UTF8 } catch { }
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
function Install-LatestPython {
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) {
        Start-Process 'https://www.python.org/downloads/windows/'
        throw 'winget is not available. The official Python download page was opened; install Python 3.10 or later and run the launcher again.'
    }
    $packageId = Find-LatestWingetPythonId
    if (-not $packageId) { throw 'Could not find the latest stable Python package in winget.' }
    Write-StartupLog "Installing latest Python package $packageId"
    $installArgs = @('install', '--id', $packageId, '--exact', '--scope', 'user', '--accept-package-agreements', '--accept-source-agreements')
    & $winget.Source @installArgs >> $startupLog 2>&1
    if ($LASTEXITCODE -ne 0) {
        $upgradeArgs = @('upgrade', '--id', $packageId, '--exact', '--scope', 'user', '--accept-package-agreements', '--accept-source-agreements')
        & $winget.Source @upgradeArgs >> $startupLog 2>&1
    }
    if ($LASTEXITCODE -ne 0) { throw "winget could not install/update $packageId (exit code $LASTEXITCODE). See $startupLog" }
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
    $versionCode = 'import sys; print("%d.%d" % sys.version_info[:2]); raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'
    foreach ($candidate in $candidates) {
        try {
            $commandArgs = @($candidate.Args) + @('-c', $versionCode)
            $version = & $candidate.File @commandArgs 2>$null
            if ($LASTEXITCODE -eq 0) {
                return @{ File = $candidate.File; Args = @($candidate.Args); Version = ($version | Select-Object -Last 1).ToString().Trim() }
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
        if (-not (Ask 'Install or update the latest stable Python available in winget? MediaForge will then rebuild its private Python environment.' 'Python runtime')) {
            Write-StartupLog 'Latest Python installation cancelled by user'
            exit
        }
        $preferredVersion = Install-LatestPython
        $basePython = Find-BasePython $preferredVersion
        if (-not $basePython) {
            Notice 'Python was installed. Windows has not refreshed its PATH in this launcher yet. Run the launcher again after signing out and back in if needed.' 'Python runtime'
            exit
        }
    } elseif (-not $basePython) {
        if (-not (Ask 'Python 3.10 or later is required. Install the latest stable Python available through winget?' 'Install Python')) {
            Write-StartupLog 'Python installation declined'
            exit
        }
        $preferredVersion = Install-LatestPython
        $basePython = Find-BasePython $preferredVersion
        if (-not $basePython) {
            Notice 'Python was installed. Run this launcher again; Windows may need a new sign-in to refresh PATH.' 'Python runtime'
            exit
        }
    }

    $venvPath = Join-Path $pythonEnvDir ("py" + $basePython.Version)
    $venvPython = Join-Path $venvPath 'Scripts\python.exe'
    $venvPythonw = Join-Path $venvPath 'Scripts\pythonw.exe'
    if (-not (Test-Path -LiteralPath $venvPython)) {
        New-Item -ItemType Directory -Path $pythonEnvDir -Force | Out-Null
        $venvArgs = @($basePython.Args) + @('-m', 'venv', $venvPath)
        & $basePython.File @venvArgs >> $startupLog 2>&1
        if ($LASTEXITCODE -ne 0) { throw "Could not create the app-local Python environment (code $LASTEXITCODE). See $startupLog" }
    }
    if (-not (Test-Path -LiteralPath $venvPythonw)) { throw 'The private Python environment has no pythonw.exe.' }

    $probeCode = 'import PyQt6, PIL, pillow_heif, piexif'
    $missing = $false
    & $venvPython -c $probeCode 2>$null
    if ($LASTEXITCODE -ne 0) { $missing = $true }
    if ($missing -and -not $UpdatePackages) {
        if (-not (Ask 'MediaForge needs PyQt6, Pillow, pillow-heif and piexif. Install the missing packages in its private app folder?' 'Python packages')) {
            Write-StartupLog 'Package installation declined'
            exit
        }
    }
    if ($missing -or $UpdatePackages) {
        Write-StartupLog 'Installing/updating app-local Python packages'
        $pipArgs = @('-m', 'pip', 'install', '--upgrade', 'PyQt6', 'Pillow', 'pillow-heif', 'piexif')
        & $venvPython @pipArgs >> $startupLog 2>&1
        if ($LASTEXITCODE -ne 0) { throw "Python package installation failed (pip exit code $LASTEXITCODE). See $startupLog" }
    }
    & $venvPython -c $probeCode 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'Required Python packages could not be verified after installation.' }
    Write-StartupLog "Starting MediaForge using Python $($basePython.Version)"
    $appArguments = '"' + $script + '"'
    if (-not [string]::IsNullOrWhiteSpace($OpenPath)) {
        $appArguments += ' "' + $OpenPath + '"'
    }
    Start-Process -FilePath $venvPythonw -ArgumentList $appArguments -WorkingDirectory $PSScriptRoot -ErrorAction Stop
} catch {
    $failure = $_.Exception.Message
    Write-StartupLog "Startup failure: $failure"
    Write-ErrorLog "Startup failure: $failure"
    [System.Windows.Forms.MessageBox]::Show($failure, 'MediaForge - startup error', 'OK', 'Error') | Out-Null
}
