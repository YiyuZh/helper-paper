param(
    [string]$CodexSkillsDir = (Join-Path $env:USERPROFILE ".codex\skills"),
    [switch]$SkipWrappers,
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
$SourceSkill = Join-Path $RepoRoot "helper-paper"
$TargetSkill = Join-Path $CodexSkillsDir "helper-paper"

function Test-PathInside {
    param(
        [Parameter(Mandatory = $true)][string]$Child,
        [Parameter(Mandatory = $true)][string]$Parent
    )
    $parentFull = [System.IO.Path]::GetFullPath($Parent).TrimEnd('\') + '\'
    $childFull = [System.IO.Path]::GetFullPath($Child).TrimEnd('\') + '\'
    return $childFull.StartsWith($parentFull, [System.StringComparison]::OrdinalIgnoreCase)
}

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
    if (-not (Test-PathInside -Child $TargetResolved -Parent $SkillsRoot)) {
        throw "Refusing to replace a path outside the Codex skills directory: $TargetResolved"
    }

    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $Backup = Join-Path $CodexSkillsDir "helper-paper.backup-$Stamp"
    if (-not $DryRun) {
        Move-Item -LiteralPath $TargetSkill -Destination $Backup
    }
    Write-Host "Backed up existing helper-paper skill to: $Backup"
}

if (-not $DryRun) {
    Copy-Item -LiteralPath $SourceSkill -Destination $TargetSkill -Recurse -Force:$Force
}

$WrapperRoot = Join-Path $RepoRoot "wrapper-skills"
$InstalledWrappers = @()
if (-not $SkipWrappers -and -not (Test-Path -LiteralPath $WrapperRoot)) {
    throw "Wrapper skills directory not found: $WrapperRoot. Use -SkipWrappers only for a helper-paper-only install."
}
if (-not $SkipWrappers -and (Test-Path -LiteralPath $WrapperRoot)) {
    Get-ChildItem -LiteralPath $WrapperRoot -Directory | ForEach-Object {
        $WrapperSource = $_.FullName
        $WrapperName = $_.Name
        $WrapperTarget = Join-Path $CodexSkillsDir $WrapperName

        if (-not (Test-Path -LiteralPath (Join-Path $WrapperSource "SKILL.md"))) {
            throw "Wrapper SKILL.md not found: $WrapperSource"
        }

        if (Test-Path -LiteralPath $WrapperTarget) {
            $WrapperResolved = (Resolve-Path -LiteralPath $WrapperTarget).Path
            if (-not (Test-PathInside -Child $WrapperResolved -Parent $SkillsRoot)) {
                throw "Refusing to replace a path outside the Codex skills directory: $WrapperResolved"
            }

            $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
            $WrapperBackup = Join-Path $CodexSkillsDir "$WrapperName.backup-$Stamp"
            if (-not $DryRun) {
                Move-Item -LiteralPath $WrapperTarget -Destination $WrapperBackup
            }
            Write-Host "Backed up existing $WrapperName skill to: $WrapperBackup"
        }

        if (-not $DryRun) {
            Copy-Item -LiteralPath $WrapperSource -Destination $WrapperTarget -Recurse -Force:$Force
        }
        $InstalledWrappers += $WrapperTarget
    }
}

Write-Host ""
if ($DryRun) {
    Write-Host "Dry run completed. No files were copied or moved."
    Write-Host ""
}
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
$SystemQuickValidate = Join-Path $env:USERPROFILE ".codex\skills\.system\skill-creator\scripts\quick_validate.py"
Write-Host "  python `"$SystemQuickValidate`" `"$TargetSkill`""
foreach ($Wrapper in $InstalledWrappers) {
    Write-Host "  python `"$SystemQuickValidate`" `"$Wrapper`""
}
Write-Host "  python `"$TargetSkill\scripts\check_translation_providers.py`" --provider auto --no-smoke"
Write-Host "  python `"$TargetSkill\scripts\check_paper_vault.py`" --root `"<your-paper-vault>\paper`""
Write-Host "  # After ChatPaper is installed under HELPER_PAPER_EXTERNAL_TOOLS_ROOT:"
Write-Host "  python `"$TargetSkill\scripts\patch_chatpaper_mimo.py`" --check"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Configure provider environment variables. See archive/example-env.md."
Write-Host "  2. Initialize a paper vault if needed:"
Write-Host "     python `"$TargetSkill\scripts\init_paper_vault.py`" --root `"<your-paper-vault>\paper`""
Write-Host "  3. In Codex chat, type: `$helper-paper start my day"
