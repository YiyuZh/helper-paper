param(
    [string]$CodexSkillsDir = (Join-Path $env:USERPROFILE ".codex\skills"),
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
$SourceSkill = Join-Path $RepoRoot "helper-paper"
$TargetSkill = Join-Path $CodexSkillsDir "helper-paper"

if (-not (Test-Path -LiteralPath $SourceSkill)) {
    throw "Source skill not found: $SourceSkill"
}

if (-not (Test-Path -LiteralPath (Join-Path $SourceSkill "SKILL.md"))) {
    throw "Source SKILL.md not found: $SourceSkill"
}

if (-not (Test-Path -LiteralPath $CodexSkillsDir)) {
    New-Item -ItemType Directory -Path $CodexSkillsDir | Out-Null
}

$SkillsRoot = (Resolve-Path -LiteralPath $CodexSkillsDir).Path

if (Test-Path -LiteralPath $TargetSkill) {
    $TargetResolved = (Resolve-Path -LiteralPath $TargetSkill).Path
    if (-not $TargetResolved.StartsWith($SkillsRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to replace a path outside the Codex skills directory: $TargetResolved"
    }

    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $Backup = Join-Path $CodexSkillsDir "helper-paper.backup-$Stamp"
    Move-Item -LiteralPath $TargetSkill -Destination $Backup
    Write-Host "Backed up existing helper-paper skill to: $Backup"
}

Copy-Item -LiteralPath $SourceSkill -Destination $TargetSkill -Recurse -Force:$Force

$WrapperRoot = Join-Path $RepoRoot "wrapper-skills"
$InstalledWrappers = @()
if (Test-Path -LiteralPath $WrapperRoot) {
    Get-ChildItem -LiteralPath $WrapperRoot -Directory | ForEach-Object {
        $WrapperSource = $_.FullName
        $WrapperName = $_.Name
        $WrapperTarget = Join-Path $CodexSkillsDir $WrapperName

        if (-not (Test-Path -LiteralPath (Join-Path $WrapperSource "SKILL.md"))) {
            throw "Wrapper SKILL.md not found: $WrapperSource"
        }

        if (Test-Path -LiteralPath $WrapperTarget) {
            $WrapperResolved = (Resolve-Path -LiteralPath $WrapperTarget).Path
            if (-not $WrapperResolved.StartsWith($SkillsRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
                throw "Refusing to replace a path outside the Codex skills directory: $WrapperResolved"
            }

            $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
            $WrapperBackup = Join-Path $CodexSkillsDir "$WrapperName.backup-$Stamp"
            Move-Item -LiteralPath $WrapperTarget -Destination $WrapperBackup
            Write-Host "Backed up existing $WrapperName skill to: $WrapperBackup"
        }

        Copy-Item -LiteralPath $WrapperSource -Destination $WrapperTarget -Recurse -Force:$Force
        $InstalledWrappers += $WrapperTarget
    }
}

Write-Host ""
Write-Host "Installed helper-paper skill to:"
Write-Host "  $TargetSkill"
if ($InstalledWrappers.Count -gt 0) {
    Write-Host ""
    Write-Host "Installed wrapper skills:"
    foreach ($Wrapper in $InstalledWrappers) {
        Write-Host "  $Wrapper"
    }
}
Write-Host ""
Write-Host "Recommended validation:"
Write-Host "  python `"$CodexSkillsDir\.system\skill-creator\scripts\quick_validate.py`" `"$TargetSkill`""
foreach ($Wrapper in $InstalledWrappers) {
    Write-Host "  python `"$CodexSkillsDir\.system\skill-creator\scripts\quick_validate.py`" `"$Wrapper`""
}
Write-Host "  python `"$TargetSkill\scripts\check_translation_providers.py`" --provider auto --no-smoke"
Write-Host "  python `"$TargetSkill\scripts\patch_chatpaper_mimo.py`" --check"
Write-Host "  python `"$TargetSkill\scripts\check_paper_vault.py`" --root `"E:\sci\commercial science\commercialscience\paper`""
