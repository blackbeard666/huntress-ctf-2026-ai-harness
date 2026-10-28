# Huntress Script Triage -- inert typed PowerShell-to-Python handoff precursor
# This file is an analyst-visible execution plan. It does not launch a process.
$HandoffId = 'PSPY-BD0582CA8883E908'
$Interpreter = 'python.exe'
$NextStage = 'pyarmor-pyinstaller-recovered.py'
$ArgumentVector = @($NextStage, '--handoff-id', $HandoffId)
$ExecutionPlan = [pscustomobject]@{
    Adapter = 'Start-Process'
    Interpreter = $Interpreter
    Arguments = $ArgumentVector
    HandoffId = $HandoffId
    Executed = $false
}

$ExecutionPlan
