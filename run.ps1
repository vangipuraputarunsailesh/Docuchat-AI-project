param(
    [switch]$Build,
    [switch]$Detach,
    [int]$Port = 8501,
    [string]$Image = "docuchat",
    [string]$Name = "docuchat"
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$envFile = Join-Path $root ".env"
if (!(Test-Path $envFile)) {
    Write-Host "Missing .env. Copy .env.example to .env and set OPENAI_API_KEY." -ForegroundColor Yellow
    exit 1
}

# Ensure persistent vector store folder exists
$chromaDir = Join-Path $root "chroma_db"
New-Item -ItemType Directory -Force $chromaDir | Out-Null

# Build image if requested or not present
function Test-ImageExists($image) {
    try {
        docker image inspect $image | Out-Null
        return $true
    } catch { return $false }
}

if ($Build -or -not (Test-ImageExists $Image)) {
    Write-Host "Building image '$Image'..." -ForegroundColor Cyan
    docker build -t $Image $root
}

# If a container with the same name exists, remove it
$existing = docker ps -a --format "{{.Names}}" | Where-Object { $_ -eq $Name }
if ($existing) {
    Write-Host "Removing existing container '$Name'..." -ForegroundColor Yellow
    docker rm -f $Name | Out-Null
}

$volSpec = "$chromaDir:/app/chroma_db"
$commonArgs = @(
    "-p", "$Port:8501",
    "--env-file", $envFile,
    "-v", $volSpec,
    "--name", $Name,
    $Image
)

if ($Detach) {
    Write-Host "Starting container in background at http://localhost:$Port ..." -ForegroundColor Green
    docker run -d @commonArgs | Out-Null
} else {
    Write-Host "Starting container (attached). Press Ctrl+C to stop. Open http://localhost:$Port" -ForegroundColor Green
    docker run --rm @commonArgs
}
