# Windows launcher: starts the GUI without a console and offers Python installation if missing.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
$logDir = Join-Path $env:USERPROFILE '.fotoverktyg_studio\logs'
try { New-Item -ItemType Directory -Path $logDir -Force | Out-Null } catch { }
$startupLog = Join-Path $logDir 'startare.log'
function Write-StartupLog([string]$text) {
    try { Add-Content -LiteralPath $startupLog -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $text") -Encoding UTF8 } catch { }
}
Write-StartupLog 'Startaren öppnad'

function Notice([string]$text, [string]$title = 'Fotoverktyg') {
    [System.Windows.Forms.MessageBox]::Show($text, $title, 'OK', 'Information') | Out-Null
}
function Find-Pythonw {
    # Try the official Python launcher first; then pythonw.exe on PATH.
    foreach ($name in @('pyw.exe', 'pythonw.exe')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        try {
            $args = if ($name -eq 'pyw.exe') { @('-3', '-c', 'import sys; print(sys.version_info.major)') } else { @('-c', 'import sys; print(sys.version_info.major)') }
            $proc = Start-Process -FilePath $cmd.Source -ArgumentList $args -Wait -PassThru -WindowStyle Hidden -ErrorAction Stop
            if ($proc.ExitCode -eq 0) { return @{ File = $cmd.Source; Args = $(if ($name -eq 'pyw.exe') { @('-3') } else { @() }) } }
        } catch { }
    }
    return $null
}

try {
    $script = Join-Path $PSScriptRoot 'fotoverktyg.pyw'
    if (-not (Test-Path -LiteralPath $script)) {
        throw 'fotoverktyg.pyw saknas. Lägg startfilerna i samma mapp som appen.'
    }
    $python = Find-Pythonw
    if (-not $python) {
        Write-StartupLog 'Python saknas'
        $answer = [System.Windows.Forms.MessageBox]::Show(
            'Python 3 hittades inte. Vill du installera Python via Windows pakethanterare (winget)? Ingen installation startas utan ditt godkännande.',
            'Python saknas', 'YesNo', 'Question')
        if ($answer -ne 'Yes') { Write-StartupLog 'Pythoninstallation nekades'; exit }
        if (Get-Command winget.exe -ErrorAction SilentlyContinue) {
            # Explicit consent above. Installer is separate from this app.
            $install = Start-Process -FilePath 'winget.exe' -ArgumentList @('install', '--id', 'Python.Python.3.13', '-e', '--scope', 'user', '--accept-package-agreements', '--accept-source-agreements') -Wait -PassThru -ErrorAction Stop
            Write-StartupLog "Winget installationskod: $($install.ExitCode)"
            if ($install.ExitCode -eq 0) {
                Notice 'Python har installerats. Starta Starta_Fotoverktyg.vbs igen. Om Windows inte hittar Python direkt kan du behöva logga ut och in.'
            } else {
                Notice "Installationen kunde inte slutföras (kod $($install.ExitCode)). Installera Python manuellt från https://www.python.org/downloads/windows/"
            }
        } else {
            $answer = [System.Windows.Forms.MessageBox]::Show('Winget finns inte. Vill du öppna den officiella Python-nedladdningssidan?', 'Installera Python', 'YesNo', 'Question')
            if ($answer -eq 'Yes') { Start-Process 'https://www.python.org/downloads/windows/' }
        }
        exit
    }
    # Start-Process does not show a console with pythonw/pyw.
    Write-StartupLog "Appstart: $script med $($python.File)"
    Start-Process -FilePath $python.File -ArgumentList ($python.Args + @('"' + $script + '"')) -WorkingDirectory $PSScriptRoot -ErrorAction Stop
} catch {
    Write-StartupLog "Startfel: $($_.Exception.Message)"
    [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Fotoverktyg - startfel', 'OK', 'Error') | Out-Null
}
