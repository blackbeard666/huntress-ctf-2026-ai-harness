# @runtime Jython
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
di=DecompInterface(); di.openProgram(currentProgram)
fm=currentProgram.getFunctionManager()
out=open(getScriptArgs()[0],'w')
for a in getScriptArgs()[1:]:
    f=fm.getFunctionAt(toAddr(int(a,16)))
    if f is None:
        f=createFunction(toAddr(int(a,16)),None)
    r=di.decompileFunction(f,600,ConsoleTaskMonitor())
    out.write('// '+a+'\n'+(r.getDecompiledFunction().getC() if r.decompileCompleted() else 'FAIL '+str(r.getErrorMessage()))+'\n')
out.close()
