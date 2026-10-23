// Independent reader (System.Reflection.PortableExecutable / Metadata) for the mmnat_* fixtures: COR20 flags, machine,
// VTableFixups entries (+ slot tokens), ManagedNativeHeader signature, and every FieldRVA blob (name + hex).
using System; using System.IO; using System.Linq; using System.Reflection.Metadata; using System.Reflection.PortableExecutable;
static class O {
  static int Main(string[] a) {
    try {
      using var s = File.OpenRead(a[0]); using var pe = new PEReader(s);
      var h = pe.PEHeaders; var c = h.CorHeader; if (c == null) { Console.WriteLine("none"); return 0; }
      Console.WriteLine($"machine=0x{(ushort)h.CoffHeader.Machine:x4} flags=0x{(uint)c.Flags:x8} [{c.Flags}] ver={c.MajorRuntimeVersion}.{c.MinorRuntimeVersion} ep=0x{c.EntryPointTokenOrRelativeVirtualAddress:x8}");
      var v = c.VtableFixupsDirectory; Console.WriteLine($"vtfixups rva=0x{v.RelativeVirtualAddress:x} size={v.Size}");
      if (v.Size > 0) { var b = pe.GetSectionData(v.RelativeVirtualAddress).GetContent(0, v.Size).ToArray();
        for (int k = 0; k + 8 <= v.Size; k += 8) { int r = BitConverter.ToInt32(b, k); int n = BitConverter.ToUInt16(b, k + 4); int t = BitConverter.ToUInt16(b, k + 6);
          var sl = pe.GetSectionData(r).GetContent(0, n * ((t & 2) != 0 ? 8 : 4)).ToArray();
          Console.WriteLine($"  entry rva=0x{r:x} count={n} type=0x{t:x4} tokens=" + string.Join(",", Enumerable.Range(0, n).Select(j => "0x" + BitConverter.ToUInt32(sl, j * ((t & 2) != 0 ? 8 : 4)).ToString("x8")))); } }
      var m = c.ManagedNativeHeaderDirectory;
      Console.WriteLine($"managed_native_header rva=0x{m.RelativeVirtualAddress:x} size={m.Size}" + (m.Size >= 4 ? " sig=" + System.Text.Encoding.ASCII.GetString(pe.GetSectionData(m.RelativeVirtualAddress).GetContent(0, 3).ToArray()) : ""));
      var md = pe.GetMetadataReader();
      foreach (var fh in md.FieldDefinitions) { var f = md.GetFieldDefinition(fh); int rva = f.GetRelativeVirtualAddress(); if (rva == 0) continue;
        var td = md.GetTypeDefinition(f.GetDeclaringType());
        Console.WriteLine($"  fieldrva {md.GetString(td.Name)}::{md.GetString(f.Name)} rva=0x{rva:x}"); }
      foreach (var ih in md.ImportedMethods(pe)) Console.WriteLine("  pinvoke " + ih);
    } catch (Exception e) { Console.WriteLine("none (" + e.GetType().Name + ")"); }
    return 0;
  }
  static System.Collections.Generic.IEnumerable<string> ImportedMethods(this MetadataReader md, PEReader pe) {
    foreach (var mh in md.MethodDefinitions) { var d = md.GetMethodDefinition(mh); var imp = d.GetImport();
      if (imp.Module.IsNil) continue; yield return md.GetString(d.Name) + " -> " + md.GetString(imp.Name) + "@" + md.GetString(md.GetModuleReference(imp.Module).Name); }
  }
}
