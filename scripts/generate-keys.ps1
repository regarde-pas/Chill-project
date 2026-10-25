<#
.SYNOPSIS
    Génère une paire de clés Ed25519 pour signer les mises à jour en jeu de Cinnabar.
#>

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   GÉNÉRATEUR DE CLÉS ED25519 POUR MISES À JOUR CINNABAR   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Vérifier si python est disponible
$pythonCmd = Get-Command python.exe -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command py.exe -ErrorAction SilentlyContinue
}

# Vérifier si cargo est disponible
$cargoCmd = Get-Command cargo.exe -ErrorAction SilentlyContinue

if ($pythonCmd) {
    Write-Host "`nUtilisation de Python pour générer les clés..." -ForegroundColor Green
    & $pythonCmd.Source "$scriptDir\keygen.py" keygen
} elseif ($cargoCmd) {
    Write-Host "`nUtilisation de Cargo pour générer les clés..." -ForegroundColor Green
    # Création d'une commande via release-manifest
    & cargo run --quiet -p release-manifest -- keygen
} else {
    Write-Host "`n[INFO] Ni Python ni Cargo ne sont installés sur cette machine locale." -ForegroundColor Yellow
    Write-Host "Pas d'inquiétude ! Le workflow GitHub Actions peut générer les clés directement dans le cloud." -ForegroundColor Yellow
    Write-Host "Vous pouvez exécuter le workflow GitHub Actions pour obtenir votre paire de clés." -ForegroundColor White
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "Sauvegardez soigneusement votre clé privée (seed) !" -ForegroundColor Yellow
Write-Host "Ne partagez JAMAIS votre clé privée sur un repo public !" -ForegroundColor Red
Write-Host "==========================================================" -ForegroundColor Cyan
