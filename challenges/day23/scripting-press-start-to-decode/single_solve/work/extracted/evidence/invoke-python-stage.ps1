# Huntress Script Triage -- inert typed PowerShell-to-Python handoff precursor
# This file is an analyst-visible execution plan. It does not launch a process.
$HandoffId = 'PSPY-9CEC7B7B8293F6C8'
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
