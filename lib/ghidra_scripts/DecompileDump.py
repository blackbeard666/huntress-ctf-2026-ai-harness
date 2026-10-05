# Ghidra headless postScript (Jython): decompile every function, write C to the output path (argv[0]).
# Invoked by lib.binary.ghidra_decompile via analyzeHeadless -postScript DecompileDump.py <out.c>
# @category Huntress
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

args = getScriptArgs()
out_path = args[0] if args else "decomp.c"

ifc = DecompInterface()
ifc.openProgram(currentProgram)
monitor = ConsoleTaskMonitor()

with open(out_path, "w") as f:
    fm = currentProgram.getFunctionManager()
    for func in fm.getFunctions(True):
        try:
            res = ifc.decompileFunction(func, 60, monitor)
            if res and res.decompiledFunction:
                f.write("/* %s @ %s */\n" % (func.getName(), func.getEntryPoint()))
                f.write(res.decompiledFunction.getC())
                f.write("\n\n")
        except Exception as e:  # noqa
            f.write("/* decompile failed for %s: %s */\n" % (func.getName(), e))
