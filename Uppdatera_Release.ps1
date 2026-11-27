# MediaForge release updater (Windows / PowerShell)
# Moves the 0.0.2 release tag to the current HEAD commit and refreshes the
# GitHub release notes. Run this after every code update so the in-app
# updater offers the latest code to users.
#
# Usage:  .\Uppdatera_Release.ps1 [-NotesFile <path-to-notes.md>]
# If no notes file is given, the existing release notes are kept and only
# the tag is moved and the release is marked Latest.
param(
    [string]$NotesFile = ''
)

$ErrorActionPreference = 'Stop'
$Tag = '0.0.2'
$Remote = 'origin'

function Fail([string]$Message) {
    Write-Host "Fel: $Message" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail 'git saknas i PATH.'
}

$root = git rev-parse --show-toplevel
if (-not $root) { Fail 'Kunde inte hitta Git-repot.' }
Set-Location $root
$Branch = git symbolic-ref --quiet --short HEAD
if ($LASTEXITCODE -ne 0 -or -not $Branch) { Fail 'Frikopplad HEAD stöds inte.' }
if ($Branch -in @('main', 'master')) { Fail 'Release från main/master är spärrad.' }

$status = git status --porcelain
if ($status) { Fail 'Arbetskopian har ocommitade ändringar. Committa eller stash:a först.' }

$head = git rev-parse HEAD
Write-Host "HEAD: $head"

git fetch $Remote $Branch
if ($LASTEXITCODE -ne 0) { Fail 'Kunde inte hämta grenen från origin.' }

$remoteTip = git rev-parse FETCH_HEAD
if ($head -ne $remoteTip) {
    Fail "HEAD ($head) skiljer sig från origin/$Branch ($remoteTip). Pusha först."
}

$oldTag = git ls-remote $Remote "refs/tags/$Tag" | ForEach-Object { ($_ -split "`t")[0] }
if ($oldTag -eq $head) {
    Write-Host "Taggen $Tag pekar redan på HEAD. Inget att göra."
} else {
    git push --force $Remote "$head`:refs/tags/$Tag"
    if ($LASTEXITCODE -ne 0) { Fail 'Kunde inte flytta taggen.' }
    Write-Host "Taggen $Tag flyttad till $head"
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Fail 'gh saknas i PATH; releasen kunde inte uppdateras.'
}
if ($NotesFile) {
    if (-not (Test-Path $NotesFile)) { Fail "Anteckningsfilen hittas inte: $NotesFile" }
    gh release edit $Tag --latest --notes-file $NotesFile
} else {
    gh release edit $Tag --latest
}
if ($LASTEXITCODE -ne 0) { Fail 'Kunde inte uppdatera releasen.' }

Write-Host 'Klart. GitHub-releasen är nu uppdaterad.'
