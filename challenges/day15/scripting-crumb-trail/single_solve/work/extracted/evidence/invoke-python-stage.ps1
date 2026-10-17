# Huntress Script Triage -- inert typed PowerShell-to-Python handoff precursor
# This file is an analyst-visible execution plan. It does not launch a process.
$HandoffId = 'PSPY-EE5E5E09048DC4DB'
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
