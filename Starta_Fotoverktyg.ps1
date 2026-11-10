# Windows launcher for MediaForge. Uses an existing system Python; it never installs
# a Python runtime or creates an app-private environment. Python packages are shared per user.
param(
    [switch]$UpdatePackages,
    [Alias('InstallLatestPython')][switch]$UpdateSystemPython,
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
function Update-SystemPython([hashtable]$ExistingPython) {
    if (-not $ExistingPython) {
        throw 'No compatible system Python was found. MediaForge will not install a separate Python runtime.'
    }
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "Python $($ExistingPython.Version) is already installed, but winget is unavailable. It was left unchanged."
    }
    $packageId = "Python.Python.$($ExistingPython.Version)"
    $listedPackages = & $winget.Source list --id $packageId --exact --source winget --accept-source-agreements 2>$null | Out-String
    if ($LASTEXITCODE -ne 0 -or $listedPackages -notmatch [regex]::Escape($packageId)) {
        throw "Python $($ExistingPython.Version) is installed but is not managed by winget. It was left unchanged; no other Python was installed."
    }
    Write-StartupLog "Updating existing system Python package $packageId"
    $upgradeArgs = @('upgrade', '--id', $packageId, '--exact', '--source', 'winget', '--accept-package-agreements', '--accept-source-agreements')
    & $winget.Source @upgradeArgs >> $startupLog 2>&1
    $upgradeExitCode = $LASTEXITCODE
    $wingetCode = ([BitConverter]::ToUInt32([BitConverter]::GetBytes([int]$upgradeExitCode), 0)).ToString('X8')
    if ($upgradeExitCode -ne 0 -and $wingetCode -eq '8A15002B') {
        Write-StartupLog "No newer $packageId version is available; keeping system Python $($ExistingPython.Version)."
        return $ExistingPython.Version
    }
    if ($upgradeExitCode -ne 0 -and $wingetCode -eq '8A15010C') {
        Write-WarningLog "The Python installer was cancelled; keeping existing system Python $($ExistingPython.Version)."
        return $ExistingPython.Version
    }
    if ($upgradeExitCode -ne 0) { throw "winget could not update existing $packageId (exit code $upgradeExitCode). The existing Python was not replaced. See $startupLog" }
    return $ExistingPython.Version
}
function Find-BasePython([string]$preferredVersion = '') {
    $candidates = [System.Collections.Generic.List[object]]::new()
    $seen = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $addCandidate = {
        param([string]$candidateFile, [string[]]$candidateArgs)
        if ([string]::IsNullOrWhiteSpace($candidateFile)) { return }
        $candidateFile = $candidateFile.Trim().Trim('"')
        $key = $candidateFile + '|' + ($candidateArgs -join ' ')
        if ((Test-Path -LiteralPath $candidateFile -PathType Leaf) -and $seen.Add($key)) {
            $candidates.Add(@{ File = $candidateFile; Args = @($candidateArgs) })
        }
    }

    $py = Get-Command 'py.exe' -ErrorAction SilentlyContinue
    if ($py) {
        foreach ($line in @(& $py.Source -0p 2>$null)) {
            $match = [regex]::Match($line.ToString(), '(?i)([A-Z]:\\.*?python(?:w)?\.exe)\s*$')
            if ($match.Success) { & $addCandidate $match.Groups[1].Value ([string[]]@()) }
        }
    }

    foreach ($registryRoot in @(
        'HKCU:\Software\Python\PythonCore',
        'HKLM:\Software\Python\PythonCore',
        'HKLM:\Software\WOW6432Node\Python\PythonCore'
    )) {
        if (-not (Test-Path -LiteralPath $registryRoot)) { continue }
        foreach ($versionKey in (Get-ChildItem -LiteralPath $registryRoot -ErrorAction SilentlyContinue | Sort-Object Name -Descending)) {
            $installKeyPath = Join-Path $versionKey.PSPath 'InstallPath'
            try {
                $installKey = Get-Item -LiteralPath $installKeyPath -ErrorAction Stop
                $pythonExe = [string]$installKey.GetValue('ExecutablePath')
                if ([string]::IsNullOrWhiteSpace($pythonExe)) {
                    $installDirectory = [string]$installKey.GetValue('')
                    if ($installDirectory) { $pythonExe = Join-Path $installDirectory 'python.exe' }
                }
                & $addCandidate $pythonExe ([string[]]@())
            } catch { }
        }
    }

    foreach ($name in @('python.exe', 'python3.exe')) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command -and $command.Source -notmatch '(?i)\\Microsoft\\WindowsApps\\') {
            & $addCandidate $command.Source ([string[]]@())
        }
    }

    # Cover default python.org and Python Install Manager locations when Python
    # is installed but its installer did not add it to PATH or the registry.
    $pythonRoots = @()
    if ($env:LOCALAPPDATA) {
        $pythonRoots += (Join-Path $env:LOCALAPPDATA 'Programs\Python')
        $pythonRoots += (Join-Path $env:LOCALAPPDATA 'Python')
    }
    if ($env:ProgramFiles) { $pythonRoots += (Join-Path $env:ProgramFiles 'Python') }
    if (${env:ProgramFiles(x86)}) { $pythonRoots += (Join-Path ${env:ProgramFiles(x86)} 'Python') }
    foreach ($root in $pythonRoots) {
        if (-not (Test-Path -LiteralPath $root -PathType Container)) { continue }
        $directories = @()
        try { $directories = @(Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue) } catch { }
        foreach ($directory in $directories) {
            & $addCandidate (Join-Path $directory.FullName 'python.exe') ([string[]]@())
        }
        & $addCandidate (Join-Path $root 'python.exe') ([string[]]@())
    }

    $firstCompatiblePython = $null
    foreach ($candidate in $candidates) {
        try {
            # Avoid `python -c`: legacy Windows PowerShell quoting can corrupt
            # embedded Python source before it reaches the interpreter.
            $commandArgs = @($candidate.Args) + @('--version')
            $probeOutput = @(& $candidate.File @commandArgs 2>&1 | ForEach-Object { $_.ToString() })
            $probeExitCode = $LASTEXITCODE
            $probeText = $probeOutput -join "`n"
            $versionMatch = [regex]::Match($probeText, '(?im)\bPython\s+(\d+)\.(\d+)')
            if ($probeExitCode -eq 0 -and $versionMatch.Success) {
                $version = "$($versionMatch.Groups[1].Value).$($versionMatch.Groups[2].Value)"
                $major = [int]$versionMatch.Groups[1].Value
                $minor = [int]$versionMatch.Groups[2].Value
                if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 10)) {
                    $runtimePath = $candidate.File
                    Write-StartupLog "Found compatible system Python $version at $runtimePath"
                    $compatiblePython = @{ File = $runtimePath; Args = @(); Version = $version; Executable = $runtimePath }
                    if (-not $preferredVersion -or $version -eq $preferredVersion) { return $compatiblePython }
                    if (-not $firstCompatiblePython) { $firstCompatiblePython = $compatiblePython }
                }
            }
            Write-StartupLog "Python candidate was not compatible or could not be probed: $($candidate.File) $($candidate.Args -join ' ') (exit $probeExitCode; output: $probeText)"
        } catch {
            Write-StartupLog "Python candidate probe failed: $($candidate.File) $($candidate.Args -join ' ') ($($_.Exception.Message))"
        }
    }
    if ($firstCompatiblePython) { return $firstCompatiblePython }
    Write-StartupLog "No compatible Python found after checking $($candidates.Count) candidate(s)."
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
    if (-not $basePython) {
        throw 'No compatible system Python 3.10+ was detected. MediaForge will not install its own Python. The launcher checks the Python launcher, registry, PATH, and common user/system install folders. In Command Prompt, run `py -0p` to verify that Python 3.10+ is listed. If it is listed but MediaForge still cannot start, share Logs/launcher.log and Logs/errors.log with support.'
    }
    if ($UpdateSystemPython) {
        if (-not (Ask "Update the existing winget-managed system Python $($basePython.Version)? MediaForge will not install another Python runtime." 'Python runtime')) {
            Write-StartupLog 'System Python update cancelled by user'
            exit
        }
        $preferredVersion = Update-SystemPython $basePython
        $basePython = Find-BasePython $preferredVersion
        if (-not $basePython) {
            throw 'The existing system Python could not be found after the update attempt. No replacement Python was installed.'
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
    $refreshDue = $UpdatePackages -or (-not $packagesAvailable)
    if ($refreshDue) {
        $pipHelpArgs = @($basePython.Args) + @('-m', 'pip', 'install', '--help')
        $pipHelp = (& $basePython.File @pipHelpArgs 2>$null | Out-String)
        $pipArgs = @($basePython.Args) + @('-m', 'pip', 'install', '--user', '--upgrade')
        if ($pipHelp -match '--break-system-packages') { $pipArgs += '--break-system-packages' }
        $pipArgs += @('PyQt6', 'Pillow', 'pillow-heif', 'piexif')
        if ($UpdatePackages) { Write-StartupLog 'User requested a shared Python package refresh' }
        else { Write-StartupLog 'Required shared Python packages are missing; installing them for this user' }
        & $basePython.File @pipArgs >> $startupLog 2>&1
        $packageUpdateExitCode = $LASTEXITCODE
        & $basePython.File @probeArgs 2>$null
        $packagesAvailable = ($LASTEXITCODE -eq 0)
        if ($packageUpdateExitCode -ne 0) {
            Write-WarningLog "Shared Python package update failed (exit code $packageUpdateExitCode)"
            if (-not $packagesAvailable) { throw "Python package update failed and required packages are unavailable (exit code $packageUpdateExitCode). See $startupLog" }
            Write-StartupLog 'Continuing with the already installed packages.'
        } elseif (-not $packagesAvailable) {
            throw 'Required Python packages could not be verified after package installation.'
        }
    } else {
        Write-StartupLog 'Skipping shared Python package refresh; required packages are available and no manual refresh was requested.'
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
