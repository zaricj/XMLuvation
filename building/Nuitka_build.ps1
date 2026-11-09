<#
.SYNOPSIS
    Build XMLuvation as a standalone Windows application with Nuitka.

.DESCRIPTION
    1. Checks the prerequisites (uv, Visual Studio C++ build tools).
    2. Creates an isolated build environment in build\venv-<python> with the runtime
       dependencies from pyproject.toml plus Nuitka and pytest (your .venv is untouched).
    3. Runs the test suite against exactly the packages that will be bundled.
    4. Compiles src\main.pyw with Nuitka (icon, version info, PySide6 plugin).
    5. Assembles dist\XMLuvation-<version>\ with XMLuvation.exe and config\config.json.
    6. Starts the built exe without a window and checks that it stays up (smoke test).
    7. Optionally zips the result.

    Run from any directory:
        .\building\Nuitka_build.ps1
        .\building\Nuitka_build.ps1 -OneFile -Zip
        .\building\Nuitka_build.ps1 -CheckOnly      # prerequisites + environment, no compile

.PARAMETER Python
    Python version for the build environment (default: the version in .python-version).

.PARAMETER OneFile
    Build a single XMLuvation.exe instead of a folder. Starts slower (it unpacks itself
    on every launch); the folder build is recommended.

.PARAMETER Clean
    Delete the build environment and Nuitka's build cache first.

.PARAMETER Zip
    Also create dist\XMLuvation-<version>-win64.zip.

.PARAMETER CheckOnly
    Stop after preparing the build environment and print the Nuitka command.

.PARAMETER Jobs
    Parallel C compiler jobs (default: number of logical processors).
#>
[CmdletBinding()]
param(
    [string]$Python,
    [switch]$OneFile,
    [switch]$Clean,
    [switch]$SkipTests,
    [switch]$SkipSmokeTest,
    [switch]$Zip,
    [switch]$CheckOnly,
    [int]$Jobs = [Environment]::ProcessorCount
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $PSScriptRoot
$BuildDir = Join-Path $Root 'build'
$NuitkaOut = Join-Path $BuildDir 'nuitka'
$DistRoot = Join-Path $Root 'dist'
$Entry = Join-Path $Root 'src\main.pyw'
$Icon = Join-Path $Root 'src\xmluvation\resources\icons\xml_256px.ico'
$ConfigFile = Join-Path $Root 'src\config\config.json'
$ExeName = 'XMLuvation.exe'
$Started = Get-Date

function Write-Step([string]$Text) {
    Write-Host ''
    Write-Host "==> $Text" -ForegroundColor Cyan
}

function Invoke-Native {
    # Run a native command and stop the build if it fails.
    param([string]$FilePath, [string[]]$Arguments)
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "'$FilePath' failed with exit code $LASTEXITCODE."
    }
}

function Find-MsvcCompiler {
    # Nuitka needs MSVC on Python 3.13+ (MinGW is not supported there).
    $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
    if (-not (Test-Path $vswhere)) { return $null }
    $installs = & $vswhere -all -products * -property installationPath
    foreach ($install in $installs) {
        $compiler = Get-ChildItem -Path (Join-Path $install 'VC\Tools\MSVC') -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName 'bin\Hostx64\x64\cl.exe' } |
            Where-Object { Test-Path $_ } |
            Select-Object -First 1
        if ($compiler) { return $compiler }
    }
    return $null
}

function Test-RequiresPython([string]$Spec, [string]$Version) {
    # Understands the ">=X.Y" form used in pyproject.toml; anything else is accepted.
    if ($Spec -match '^\s*>=\s*(\d+(\.\d+)*)\s*$') {
        return ([version]$Version) -ge ([version]$Matches[1])
    }
    return $true
}

Push-Location $Root
try {
    # ------------------------------------------------------------------ prerequisites
    Write-Step 'Checking prerequisites'
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        throw 'uv was not found on PATH. Install it from https://docs.astral.sh/uv/.'
    }
    if (-not $Python) {
        $Python = (Get-Content (Join-Path $Root '.python-version') -TotalCount 1).Trim()
    }
    $compiler = Find-MsvcCompiler
    $msvcHelp = @(
        'The Visual Studio C++ compiler (cl.exe) was not found. Nuitka needs it to build on Windows.',
        'Install it with the Visual Studio Installer: Modify -> "Desktop development with C++"',
        '(keep "MSVC ... x64/x86 build tools" and a "Windows 11 SDK" selected), then run this script again.'
    ) -join [Environment]::NewLine
    if ($compiler) {
        Write-Host "MSVC compiler: $compiler"
    } elseif ($CheckOnly) {
        Write-Warning $msvcHelp
    } else {
        throw $msvcHelp
    }

    # ------------------------------------------------------------------ build environment
    $Venv = Join-Path $BuildDir "venv-$Python"
    $VenvPython = Join-Path $Venv 'Scripts\python.exe'
    if ($Clean) {
        Write-Step 'Cleaning previous build output'
        foreach ($path in @($Venv, $NuitkaOut)) {
            if (Test-Path $path) { Remove-Item $path -Recurse -Force }
        }
    }
    Write-Step "Preparing build environment (Python $Python)"
    if (-not (Test-Path $VenvPython)) {
        Invoke-Native uv @('venv', $Venv, '--python', $Python, '--seed')
    }
    $info = (& $VenvPython (Join-Path $PSScriptRoot 'build_info.py')) | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) { throw 'Reading build metadata failed.' }
    if (-not (Test-RequiresPython $info.requires_python $info.python)) {
        Write-Warning ("pyproject.toml requires Python $($info.requires_python), but the build uses " +
            "$($info.python). The tests below decide whether this version works.")
    }
    Invoke-Native uv (@('pip', 'install', '--python', $VenvPython, '--quiet') + @($info.requirements))
    Write-Host "XMLuvation $($info.version) (file version $($info.windows_version)), Python $($info.python)"

    # ------------------------------------------------------------------ Nuitka command
    $nuitkaArgs = @(
        '-m', 'nuitka',
        $(if ($OneFile) { '--onefile' } else { '--standalone' }),
        '--msvc=latest',
        '--enable-plugin=pyside6',
        '--noinclude-qt-translations',
        # pandas imports these only when a conversion asks for them, so Nuitka cannot see them.
        '--include-package=xlsxwriter',
        '--include-module=tabulate',
        '--windows-console-mode=disable',
        "--windows-icon-from-ico=$Icon",
        '--product-name=XMLuvation',
        '--file-description=XMLuvation - XPath search and CSV toolkit',
        "--product-version=$($info.windows_version)",
        "--file-version=$($info.windows_version)",
        "--output-filename=$ExeName",
        "--output-dir=$NuitkaOut",
        "--report=$(Join-Path $NuitkaOut 'compilation-report.xml')",
        "--jobs=$Jobs",
        '--lto=yes',
        '--assume-yes-for-downloads',
        $Entry
    )
    if ($CheckOnly) {
        Write-Step 'Check finished. Nuitka would run:'
        Write-Host "$VenvPython $($nuitkaArgs -join ' ')"
        return
    }

    # ------------------------------------------------------------------ tests
    if (-not $SkipTests) {
        Write-Step 'Running tests'
        $saved = @{ QT_QPA_PLATFORM = $env:QT_QPA_PLATFORM; PYTHONPATH = $env:PYTHONPATH }
        try {
            $env:QT_QPA_PLATFORM = 'offscreen'
            $env:PYTHONPATH = Join-Path $Root 'src'
            Invoke-Native $VenvPython @('-m', 'pytest', '-q', '-p', 'no:cacheprovider')
        } finally {
            $env:QT_QPA_PLATFORM = $saved.QT_QPA_PLATFORM
            $env:PYTHONPATH = $saved.PYTHONPATH
        }
    }

    # ------------------------------------------------------------------ compile
    Write-Step "Compiling with Nuitka ($(if ($OneFile) { 'single file' } else { 'folder' })) - this takes a while"
    Invoke-Native $VenvPython $nuitkaArgs

    # ------------------------------------------------------------------ assemble dist
    Write-Step 'Assembling the distribution'
    $Dist = Join-Path $DistRoot "XMLuvation-$($info.version)"
    if (Test-Path $Dist) { Remove-Item $Dist -Recurse -Force }
    if ($OneFile) {
        New-Item -ItemType Directory -Path $Dist | Out-Null
        Copy-Item (Join-Path $NuitkaOut $ExeName) $Dist
    } else {
        $built = Join-Path $NuitkaOut 'main.dist'
        if (-not (Test-Path (Join-Path $built $ExeName))) { throw "Nuitka output not found in $built." }
        New-Item -ItemType Directory -Path $DistRoot -Force | Out-Null
        Copy-Item $built $Dist -Recurse
    }
    # The app reads and writes <exe folder>\config\config.json (see xmluvation\app\paths.py).
    $DistConfig = Join-Path $Dist 'config'
    New-Item -ItemType Directory -Path $DistConfig -Force | Out-Null
    if (Test-Path $ConfigFile) {
        Copy-Item $ConfigFile $DistConfig
    } else {
        Write-Warning "No $ConfigFile; the app starts with an empty configuration."
    }
    $Exe = Join-Path $Dist $ExeName

    # ------------------------------------------------------------------ smoke test
    if (-not $SkipSmokeTest) {
        Write-Step 'Smoke test: starting the built app without a window'
        $savedPlatform = $env:QT_QPA_PLATFORM
        $env:QT_QPA_PLATFORM = 'offscreen'
        try {
            $process = Start-Process -FilePath $Exe -PassThru
        } finally {
            $env:QT_QPA_PLATFORM = $savedPlatform
        }
        if ($process.WaitForExit(10000)) {
            throw ("The built app exited during startup (exit code $($process.ExitCode)). " +
                'Check the log in %LOCALAPPDATA% (XMLuvation\logs) and build\nuitka\compilation-report.xml.')
        }
        Stop-Process -Id $process.Id -Force
        Write-Host 'The app started and kept running for 10 seconds.'
    }

    # ------------------------------------------------------------------ zip
    $Archive = $null
    if ($Zip) {
        Write-Step 'Creating zip archive'
        $Archive = Join-Path $DistRoot "XMLuvation-$($info.version)-win64.zip"
        if (Test-Path $Archive) { Remove-Item $Archive -Force }
        Compress-Archive -Path $Dist -DestinationPath $Archive
    }

    # ------------------------------------------------------------------ summary
    $sizeMb = (Get-ChildItem $Dist -Recurse -File | Measure-Object Length -Sum).Sum / 1MB
    $elapsed = (Get-Date) - $Started
    Write-Step 'Build finished'
    Write-Host ("App:      {0}" -f $Exe)
    Write-Host ("Size:     {0:N0} MB" -f $sizeMb)
    if ($Archive) { Write-Host ("Archive:  {0}" -f $Archive) }
    Write-Host ("Duration: {0:mm\:ss}" -f $elapsed)
} finally {
    Pop-Location
}
