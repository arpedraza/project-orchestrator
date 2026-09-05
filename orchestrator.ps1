[CmdletBinding()]
param(
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet('doctor','smoke-test','init','scan','sync','plan','status','handoff','checkpoint','resume','run-start','run-event','run-end')]
    [string]$Command,

    [string]$ProjectRoot = $env:PROJECT_ROOT,
    [string]$SkillsRoot = $env:SKILLS_ROOT,
    [string]$OrchestratorHome = $env:ORCHESTRATOR_HOME,

    [string]$ProjectId,
    [string]$Name,
    [string]$Objective,
    [string]$WorkId,

    [string]$ExecutorId = 'chatgpt',
    [ValidateSet('human','agent','automation','external')]
    [string]$ExecutorType = 'agent',

    [string]$RunId,
    [ValidateSet('PASS','FAIL_PRE_EXECUTION','FAIL_PRE_WRITE','FAIL_POST_WRITE','FAIL_ROLLBACK_PASS','RECOVERED_VALIDATED','CANCELLED')]
    [string]$Classification,
    [string]$Cause,
    [string]$Summary,
    [string]$EventKind = 'INFO',
    [string]$Message,

    [string[]]$Work = @(),
    [string[]]$AuthorityRef = @(),
    [string[]]$ModifyPath = @(),
    [string[]]$NewPath = @(),
    [string[]]$DeletePath = @(),
    [string[]]$ProtectedPath = @(),
    [string[]]$EvidenceRef = @(),
    [string[]]$IssueRef = @(),
    [string[]]$DecisionRef = @(),
    [string[]]$Output = @(),
    [string[]]$File = @()
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($OrchestratorHome)) {
    $OrchestratorHome = $PSScriptRoot
}
$OrchestratorHome = [System.IO.Path]::GetFullPath($OrchestratorHome)

function Assert-PathExists {
    param([string]$Path, [string]$Label)
    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path)) {
        throw "$Label not found: $Path"
    }
}

function Require-Value {
    param([string]$Value, [string]$Label)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "$Label is required for command '$Command'."
    }
}

function Resolve-PythonRunner {
    $Candidates = @(
        [pscustomobject]@{ Command = 'py'; Prefix = @('-3') },
        [pscustomobject]@{ Command = 'python'; Prefix = @() },
        [pscustomobject]@{ Command = 'python3'; Prefix = @() }
    )

    foreach ($Candidate in $Candidates) {
        $Found = Get-Command $Candidate.Command -ErrorAction SilentlyContinue
        if ($null -eq $Found) { continue }
        & $Found.Source @($Candidate.Prefix) -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" *> $null
        if ($LASTEXITCODE -eq 0) {
            return [pscustomobject]@{
                Path = $Found.Source
                Prefix = @($Candidate.Prefix)
                Display = $Candidate.Command
            }
        }
    }

    throw 'Python 3.10+ was not found. The PowerShell harness installs nothing; the current orchestrator engine requires an existing Python 3.10+ runtime.'
}

function Invoke-OrchestratorPython {
    param([string[]]$Arguments)
    & $script:Python.Path @($script:Python.Prefix + $Arguments)
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE."
    }
}

function Invoke-OrchestratorPythonCapture {
    param([string[]]$Arguments)
    $Lines = @(& $script:Python.Path @($script:Python.Prefix + $Arguments) 2>&1)
    $ExitCode = $LASTEXITCODE
    $Text = [string]::Join([Environment]::NewLine, @($Lines | ForEach-Object { $_.ToString() }))
    if ($ExitCode -ne 0) {
        throw "Python command failed with exit code $ExitCode.`n$Text"
    }
    return $Text
}

function Write-Utf8NoBom {
    param([string]$Path, [string]$Text)
    $Parent = Split-Path -Parent $Path
    if ($Parent) { New-Item -ItemType Directory -Path $Parent -Force | Out-Null }
    $Encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Text + [Environment]::NewLine, $Encoding)
}

function Add-RepeatedArguments {
    param(
        [System.Collections.Generic.List[string]]$Target,
        [string]$Flag,
        [string[]]$Values
    )
    foreach ($Value in @($Values)) {
        if (-not [string]::IsNullOrWhiteSpace($Value)) {
            $Target.Add($Flag)
            $Target.Add($Value)
        }
    }
}

function Require-ProjectRoot {
    Require-Value $ProjectRoot 'ProjectRoot'
    $script:ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
}

try {
    Assert-PathExists $OrchestratorHome 'OrchestratorHome'
    Assert-PathExists (Join-Path $OrchestratorHome 'scripts') 'Orchestrator scripts directory'
    $script:Python = Resolve-PythonRunner

    switch ($Command) {
        'doctor' {
            Write-Host 'Project Orchestrator Local Doctor'
            Write-Host ''
            Write-Host "[PASS] PowerShell $($PSVersionTable.PSVersion)"
            Write-Host "[PASS] Orchestrator home: $OrchestratorHome"
            $Version = Invoke-OrchestratorPythonCapture @('-c', 'import sys; print(".".join(map(str,sys.version_info[:3])))')
            Write-Host "[PASS] Python $Version via $($script:Python.Display)"
            foreach ($Relative in @(
                'scripts\project_docs.py',
                'scripts\orchestrate_project.py',
                'scripts\executor_continuity.py',
                'scripts\smoke_test.py',
                'profiles\default-policy.json'
            )) {
                Assert-PathExists (Join-Path $OrchestratorHome $Relative) $Relative
                Write-Host "[PASS] $Relative"
            }
            $Git = Get-Command git -ErrorAction SilentlyContinue
            if ($null -eq $Git) {
                Write-Host '[INFO] Git executable not found. Git snapshots will be unavailable, but core local orchestration can still run.'
            }
            else {
                Write-Host "[PASS] Git available: $($Git.Source)"
            }
            Write-Host ''
            Write-Host 'RESULT: PASS / STRUCTURAL'
            break
        }

        'smoke-test' {
            Invoke-OrchestratorPython @((Join-Path $OrchestratorHome 'scripts\smoke_test.py'))
            break
        }

        'init' {
            Require-ProjectRoot
            Require-Value $ProjectId 'ProjectId'
            Require-Value $Name 'Name'
            Require-Value $Objective 'Objective'
            New-Item -ItemType Directory -Path $script:ProjectRoot -Force | Out-Null
            Invoke-OrchestratorPython @(
                (Join-Path $OrchestratorHome 'scripts\project_docs.py'),
                '--root', $script:ProjectRoot,
                'init',
                '--project-id', $ProjectId,
                '--name', $Name,
                '--objective', $Objective
            )
            break
        }

        'scan' {
            Require-ProjectRoot
            Require-Value $SkillsRoot 'SkillsRoot'
            $SkillsRoot = [System.IO.Path]::GetFullPath($SkillsRoot)
            Assert-PathExists $SkillsRoot 'SkillsRoot'
            $RegistryDir = Join-Path $script:ProjectRoot '.orchestrator\registry'
            New-Item -ItemType Directory -Path $RegistryDir -Force | Out-Null
            $InventoryPath = Join-Path $RegistryDir 'local-inventory.json'
            $RegistryPath = Join-Path $RegistryDir 'capability-registry.json'
            $Inventory = Invoke-OrchestratorPythonCapture @(
                (Join-Path $OrchestratorHome 'scripts\scan_skills.py'),
                $SkillsRoot,
                '--format', 'json'
            )
            Write-Utf8NoBom $InventoryPath $Inventory
            $Registry = Invoke-OrchestratorPythonCapture @(
                (Join-Path $OrchestratorHome 'scripts\build_registry.py'),
                '--inventory', $InventoryPath,
                '--catalog-dir', (Join-Path $OrchestratorHome 'catalog'),
                '--format', 'json'
            )
            Write-Utf8NoBom $RegistryPath $Registry
            Write-Host "[PASS] Inventory: $InventoryPath"
            Write-Host "[PASS] Registry:  $RegistryPath"
            break
        }

        'sync' {
            Require-ProjectRoot
            Invoke-OrchestratorPython @(
                (Join-Path $OrchestratorHome 'scripts\project_docs.py'),
                '--root', $script:ProjectRoot,
                'sync'
            )
            break
        }

        'plan' {
            Require-ProjectRoot
            Invoke-OrchestratorPython @(
                (Join-Path $OrchestratorHome 'scripts\orchestrate_project.py'),
                '--root', $script:ProjectRoot
            )
            break
        }

        'status' {
            Require-ProjectRoot
            Invoke-OrchestratorPython @(
                (Join-Path $OrchestratorHome 'scripts\project_docs.py'),
                '--root', $script:ProjectRoot,
                'render'
            )
            $StatusPath = Join-Path $script:ProjectRoot 'docs\00-project-control\status.md'
            Assert-PathExists $StatusPath 'Generated status'
            Get-Content -LiteralPath $StatusPath
            break
        }

        'handoff' {
            Require-ProjectRoot
            Require-Value $WorkId 'WorkId'
            Invoke-OrchestratorPython @(
                (Join-Path $OrchestratorHome 'scripts\project_docs.py'),
                '--root', $script:ProjectRoot,
                'handoff', $WorkId
            )
            break
        }

        'checkpoint' {
            Require-ProjectRoot
            $Args = [System.Collections.Generic.List[string]]::new()
            foreach ($Item in @(
                (Join-Path $OrchestratorHome 'scripts\executor_continuity.py'),
                '--root', $script:ProjectRoot,
                'checkpoint',
                '--executor-id', $ExecutorId,
                '--executor-type', $ExecutorType
            )) { $Args.Add([string]$Item) }
            if (-not [string]::IsNullOrWhiteSpace($Objective)) {
                $Args.Add('--objective'); $Args.Add($Objective)
            }
            Invoke-OrchestratorPython $Args.ToArray()
            $Latest = Join-Path $script:ProjectRoot '.orchestrator\checkpoints\latest.md'
            Assert-PathExists $Latest 'Latest checkpoint'
            Write-Host ''
            Get-Content -LiteralPath $Latest
            break
        }

        'resume' {
            Require-ProjectRoot
            Invoke-OrchestratorPython @(
                (Join-Path $OrchestratorHome 'scripts\executor_continuity.py'),
                '--root', $script:ProjectRoot,
                'resume'
            )
            $Latest = Join-Path $script:ProjectRoot '.orchestrator\checkpoints\latest.md'
            Assert-PathExists $Latest 'Latest checkpoint'
            Write-Host ''
            Get-Content -LiteralPath $Latest
            break
        }

        'run-start' {
            Require-ProjectRoot
            Require-Value $Objective 'Objective'
            $Args = [System.Collections.Generic.List[string]]::new()
            foreach ($Item in @(
                (Join-Path $OrchestratorHome 'scripts\executor_continuity.py'),
                '--root', $script:ProjectRoot,
                'run-start',
                '--executor-id', $ExecutorId,
                '--executor-type', $ExecutorType,
                '--objective', $Objective
            )) { $Args.Add([string]$Item) }
            Add-RepeatedArguments $Args '--work' $Work
            Add-RepeatedArguments $Args '--authority-ref' $AuthorityRef
            Add-RepeatedArguments $Args '--modify' $ModifyPath
            Add-RepeatedArguments $Args '--new' $NewPath
            Add-RepeatedArguments $Args '--delete' $DeletePath
            Add-RepeatedArguments $Args '--protected' $ProtectedPath
            Invoke-OrchestratorPython $Args.ToArray()
            break
        }

        'run-event' {
            Require-ProjectRoot
            Require-Value $RunId 'RunId'
            Require-Value $Message 'Message'
            $Args = [System.Collections.Generic.List[string]]::new()
            foreach ($Item in @(
                (Join-Path $OrchestratorHome 'scripts\executor_continuity.py'),
                '--root', $script:ProjectRoot,
                'run-event',
                '--run-id', $RunId,
                '--kind', $EventKind,
                '--message', $Message
            )) { $Args.Add([string]$Item) }
            Add-RepeatedArguments $Args '--ref' $Work
            Invoke-OrchestratorPython $Args.ToArray()
            break
        }

        'run-end' {
            Require-ProjectRoot
            Require-Value $RunId 'RunId'
            Require-Value $Classification 'Classification'
            Require-Value $Summary 'Summary'
            $Args = [System.Collections.Generic.List[string]]::new()
            foreach ($Item in @(
                (Join-Path $OrchestratorHome 'scripts\executor_continuity.py'),
                '--root', $script:ProjectRoot,
                'run-end',
                '--run-id', $RunId,
                '--classification', $Classification,
                '--summary', $Summary
            )) { $Args.Add([string]$Item) }
            if (-not [string]::IsNullOrWhiteSpace($Cause)) { $Args.Add('--cause'); $Args.Add($Cause) }
            Add-RepeatedArguments $Args '--file' $File
            Add-RepeatedArguments $Args '--output' $Output
            Add-RepeatedArguments $Args '--evidence-ref' $EvidenceRef
            Add-RepeatedArguments $Args '--issue-ref' $IssueRef
            Add-RepeatedArguments $Args '--decision-ref' $DecisionRef
            Invoke-OrchestratorPython $Args.ToArray()
            Invoke-OrchestratorPython @(
                (Join-Path $OrchestratorHome 'scripts\executor_continuity.py'),
                '--root', $script:ProjectRoot,
                'checkpoint',
                '--executor-id', $ExecutorId,
                '--executor-type', $ExecutorType,
                '--objective', "Resume after $RunId"
            )
            Write-Host "[PASS] Terminal run recorded and checkpoint refreshed."
            break
        }
    }
}
catch {
    Write-Error $_.Exception.Message
    exit 2
}
