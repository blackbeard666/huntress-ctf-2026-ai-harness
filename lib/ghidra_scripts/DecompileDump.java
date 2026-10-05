// Ghidra headless postScript (Java — runs natively, no PyGhidra needed): decompile every function,
// write C to the output path (scriptArgs[0]). Invoked by lib.binary.ghidra_decompile.
// @category Huntress
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DecompileDump extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String outPath = (args.length > 0) ? args[0] : "decomp.c";
        DecompInterface ifc = new DecompInterface();
        ifc.openProgram(currentProgram);
        try (PrintWriter w = new PrintWriter(new FileWriter(outPath))) {
            FunctionManager fm = currentProgram.getFunctionManager();
            FunctionIterator it = fm.getFunctions(true);
            while (it.hasNext() && !monitor.isCancelled()) {
                Function f = it.next();
                try {
                    DecompileResults res = ifc.decompileFunction(f, 60, monitor);
                    if (res != null && res.getDecompiledFunction() != null) {
                        w.println("/* " + f.getName() + " @ " + f.getEntryPoint() + " */");
                        w.println(res.getDecompiledFunction().getC());
                        w.println();
                    }
                } catch (Exception e) {
                    w.println("/* decompile failed for " + f.getName() + ": " + e.getMessage() + " */");
                }
            }
        }
    }
}
