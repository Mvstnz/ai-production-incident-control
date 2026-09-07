param([switch]$InfrastructureOnly,[switch]$DeployOnly)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$apicBootstrapArgs = @('scripts/bootstrap.py')
if ($InfrastructureOnly) { $apicBootstrapArgs += '--infrastructure-only' }
if ($DeployOnly) { $apicBootstrapArgs += '--deploy-only' }
rtk proxy python @apicBootstrapArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
