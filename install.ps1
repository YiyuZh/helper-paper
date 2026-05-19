param(
    [string]$CodexSkillsDir = $(if ($env:HELPER_PAPER_CODEX_SKILLS_DIR) { $env:HELPER_PAPER_CODEX_SKILLS_DIR } else { Join-Path $env:USERPROFILE ".codex\skills" }),
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

function Assert-SkillSource {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Source skill not found: $Path"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $Path "SKILL.md"))) {
        throw "Source SKILL.md not found: $Path"
    }
}

function Install-SkillDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Target,
        [Parameter(Mandatory = $true)][string]$SkillsRoot,
        [Parameter(Mandatory = $true)][string]$Name
    )

    Assert-SkillSource -Path $Source
    $targetParent = Split-Path -Parent $Target
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backup = Join-Path $targetParent "$Name.backup-$stamp"
    $staging = Join-Path $targetParent ".$Name.installing-$stamp"

    if ($DryRun) {
        Write-Host "[DryRun] Would install $Name"
        Write-Host "  Source: $Source"
        Write-Host "  Target: $Target"
        if (Test-Path -LiteralPath $Target) {
            Write-Host "  Would back up existing target to: $backup"
        }
        return $Target
    }

    if (-not (Test-Path -LiteralPath $targetParent)) {
        New-Item -ItemType Directory -Path $targetParent | Out-Null
    }

    $resolvedParent = (Resolve-Path -LiteralPath $targetParent).Path
    if (-not (Test-PathInside -Child $Target -Parent $SkillsRoot)) {
        throw "Refusing to install outside the Codex skills directory: $Target"
    }
    if (Test-Path -LiteralPath $staging) {
        Remove-Item -LiteralPath $staging -Recurse -Force
    }

    Copy-Item -LiteralPath $Source -Destination $staging -Recurse -Force:$Force
    if (-not (Test-Path -LiteralPath (Join-Path $staging "SKILL.md"))) {
        Remove-Item -LiteralPath $staging -Recurse -Force
        throw "Staged install missing SKILL.md for $Name"
    }

    $targetExisted = Test-Path -LiteralPath $Target
    $madeBackup = $false
    try {
        if ($targetExisted) {
            $targetResolved = (Resolve-Path -LiteralPath $Target).Path
            if (-not (Test-PathInside -Child $targetResolved -Parent $SkillsRoot)) {
                throw "Refusing to replace a path outside the Codex skills directory: $targetResolved"
            }
            Move-Item -LiteralPath $Target -Destination $backup
            $madeBackup = $true
            Write-Host "Backed up existing $Name skill to: $backup"
        }
        Move-Item -LiteralPath $staging -Destination $Target
    } catch {
        if (((-not $targetExisted) -or $madeBackup) -and (Test-Path -LiteralPath $Target)) {
            Remove-Item -LiteralPath $Target -Recurse -Force
        }
        if ($madeBackup -and (Test-Path -LiteralPath $backup)) {
            Move-Item -LiteralPath $backup -Destination $Target
        }
        if (Test-Path -LiteralPath $staging) {
            Remove-Item -LiteralPath $staging -Recurse -Force
        }
        throw
    }

    return $Target
}

Assert-SkillSource -Path $SourceSkill

if (-not $DryRun -and -not (Test-Path -LiteralPath $CodexSkillsDir)) {
    New-Item -ItemType Directory -Path $CodexSkillsDir | Out-Null
}

if ($DryRun) {
    $SkillsRoot = [System.IO.Path]::GetFullPath($CodexSkillsDir)
} else {
    $SkillsRoot = (Resolve-Path -LiteralPath $CodexSkillsDir).Path
}

$InstalledSkill = Install-SkillDirectory -Source $SourceSkill -Target $TargetSkill -SkillsRoot $SkillsRoot -Name "helper-paper"

$WrapperRoot = Join-Path $RepoRoot "wrapper-skills"
$InstalledWrappers = @()
if (-not $SkipWrappers -and -not (Test-Path -LiteralPath $WrapperRoot)) {
    throw "Wrapper skills directory not found: $WrapperRoot. Use -SkipWrappers only for a helper-paper-only install."
}
if (-not $SkipWrappers -and (Test-Path -LiteralPath $WrapperRoot)) {
    Get-ChildItem -LiteralPath $WrapperRoot -Directory | ForEach-Object {
        $wrapperSource = $_.FullName
        $wrapperName = $_.Name
        $wrapperTarget = Join-Path $CodexSkillsDir $wrapperName
        $InstalledWrappers += Install-SkillDirectory -Source $wrapperSource -Target $wrapperTarget -SkillsRoot $SkillsRoot -Name $wrapperName
    }
}

Write-Host ""
if ($DryRun) {
    Write-Host "Dry run completed. No files or directories were created, copied, moved, or deleted."
    Write-Host ""
}
if ($DryRun) {
    Write-Host "Would install helper-paper skill to:"
} else {
    Write-Host "Installed helper-paper skill to:"
}
Write-Host "  $InstalledSkill"
if ($InstalledWrappers.Count -gt 0) {
    Write-Host ""
    if ($DryRun) {
        Write-Host "Would install wrapper skills:"
    } else {
        Write-Host "Installed wrapper skills:"
    }
    foreach ($wrapper in $InstalledWrappers) {
        Write-Host "  $wrapper"
    }
}
Write-Host ""
if ($DryRun) {
    Write-Host "Validation commands after a real install:"
} else {
    Write-Host "Recommended validation:"
}
$SystemQuickValidate = Join-Path $env:USERPROFILE ".codex\skills\.system\skill-creator\scripts\quick_validate.py"
Write-Host "  python `"$SystemQuickValidate`" `"$InstalledSkill`""
foreach ($wrapper in $InstalledWrappers) {
    Write-Host "  python `"$SystemQuickValidate`" `"$wrapper`""
}
Write-Host "  python `"$InstalledSkill\scripts\check_translation_providers.py`" --provider auto --no-smoke"
Write-Host "  python `"$InstalledSkill\scripts\check_paper_vault.py`" --root `"<your-paper-vault>\paper`""
Write-Host "  # After ChatPaper is installed under HELPER_PAPER_EXTERNAL_TOOLS_ROOT:"
Write-Host "  python `"$InstalledSkill\scripts\patch_chatpaper_mimo.py`" --check"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Configure provider environment variables. See archive/example-env.md."
Write-Host "  2. Initialize a paper vault if needed:"
Write-Host "     python `"$InstalledSkill\scripts\init_paper_vault.py`" --root `"<your-paper-vault>\paper`""
Write-Host "  3. In Codex chat, type: `$helper-paper start my day"
