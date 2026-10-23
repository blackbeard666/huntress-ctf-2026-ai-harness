// dnprot oracle: System.Reflection.Metadata (BCL ECMA-335 reader) + System.Reflection.Emit.OpCodes for IL validity, and
// for HCFG the REAL runtime: load the assembly, run its module constructor (<Module>..cctor = the anti-tamper decrypt),
// read every static byte[]/string field + ldstr literal and parse an HCFG blob (base64 tried for strings). Not dnfile.
using System; using System.Collections.Generic; using System.IO; using System.Linq; using System.Reflection;
using System.Reflection.Emit; using System.Reflection.Metadata; using System.Reflection.PortableExecutable;
using System.Reflection.Metadata.Ecma335; using System.Runtime.CompilerServices; using System.Text; using System.Text.Json;
static class O {
  static readonly Dictionary<string, string> Markers = new() { ["ConfusedByAttribute"] = "ConfuserEx",
    ["DotfuscatorAttribute"] = "Dotfuscator", ["BabelAttribute"] = "Babel", ["BabelObfuscatorAttribute"] = "Babel",
    ["PoweredByAttribute"] = "SmartAssembly", ["ObfuscatedByGoliath"] = "Goliath.NET", ["YanoAttribute"] = "Yano",
    ["ProcessedByXenocode"] = "Xenocode", ["CryptoObfuscatorAttribute"] = "Crypto Obfuscator",
    ["NETGuardAttribute"] = "NETGuard", ["ObfuscatedByAgileDotNetAttribute"] = "Agile.NET",
    ["NineRays.Obfuscator.Evaluation"] = "Spices.Net" };
  static Dictionary<short, OpCode> Ops = typeof(OpCodes).GetFields().Select(f => (OpCode)f.GetValue(null)).ToDictionary(o => o.Value);
  static bool ValidIL(byte[] il) {
    int p = 0; if (il.Length == 0) return false;
    while (p < il.Length) {
      short v = il[p]; int n = 1;
      if (v == 0xFE) { if (p + 1 >= il.Length) return false; v = (short)(0xFE00 | il[p + 1]); n = 2; }
      if (!Ops.TryGetValue(v, out var op) || op.OpCodeType == OpCodeType.Nternal) return false;
      p += n;
      switch (op.OperandType) {
        case OperandType.InlineNone: break;
        case OperandType.ShortInlineBrTarget: case OperandType.ShortInlineI: case OperandType.ShortInlineVar: p += 1; break;
        case OperandType.InlineVar: p += 2; break;
        case OperandType.InlineI8: case OperandType.InlineR: p += 8; break;
        case OperandType.InlineSwitch: if (p + 4 > il.Length) return false; p += 4 + 4 * BitConverter.ToInt32(il, p); break;
        default: p += 4; break;
      }
    }
    return p == il.Length;
  }
  static bool Bad(string s) => s.Any(c => c < 0x20 || c > 0x7e);
  static string Hcfg(byte[] b, out int at) {
    at = -1;
    for (int i = 0; i + 12 <= b.Length; i++) {
      if (b[i] != 'H' || b[i + 1] != 'C' || b[i + 2] != 'F' || b[i + 3] != 'G') continue;
      int k = b[i + 5], n = BitConverter.ToUInt16(b, i + 6); if (i + 12 + n > b.Length) continue;
      var plain = b.Skip(i + 12).Take(n).Select(x => (byte)(x ^ k)).ToArray();
      if (System.IO.Hashing.Crc32.HashToUInt32(plain) != BitConverter.ToUInt32(b, i + 8)) continue;
      at = i; return Encoding.UTF8.GetString(plain);
    }
    return null;
  }
  static int Main(string[] a) {
    var raw = File.ReadAllBytes(a[0]); var R = new Dictionary<string, object>();
    string[] keys = { "obfuscator", "obfuscator_marker", "has_suppress_ildasm", "renamed_types", "module_cctor", "encrypted_bodies", "cctor_decrypts_bodies" };
    PEReader pe; MetadataReader md;
    try { pe = new PEReader(new MemoryStream(raw)); if (!pe.HasMetadata) throw new Exception(); md = pe.GetMetadataReader(); }
    catch { Console.WriteLine(JsonSerializer.Serialize(new { facts = keys.ToDictionary(k => k, k => "none"), hcfg = (object)null })); return 0; }
    string obf = "none", marker = "none"; bool sup = false;
    foreach (var h in md.CustomAttributes) {
      var ca = md.GetCustomAttribute(h); string tn;
      if (ca.Constructor.Kind == HandleKind.MethodDefinition) tn = md.GetString(md.GetTypeDefinition(md.GetMethodDefinition((MethodDefinitionHandle)ca.Constructor).GetDeclaringType()).Name);
      else { var mr = md.GetMemberReference((MemberReferenceHandle)ca.Constructor); tn = mr.Parent.Kind == HandleKind.TypeReference ? md.GetString(md.GetTypeReference((TypeReferenceHandle)mr.Parent).Name) : ""; }
      if (tn == "SuppressIldasmAttribute") sup = true;
      if (Markers.TryGetValue(tn, out var fam) && obf == "none") {
        obf = fam; var br = md.GetBlobReader(ca.Value);
        if (br.Length > 3 && br.ReadUInt16() == 1) { var s = br.ReadSerializedString(); marker = s ?? fam; } else marker = fam;
      }
    }
    int renamed = 0, enc = 0; bool mcctor = false;
    foreach (var th in md.TypeDefinitions) {
      var td = md.GetTypeDefinition(th); var name = md.GetString(td.Name);
      if (name == "<Module>") { mcctor = td.GetMethods().Any(m => md.GetString(md.GetMethodDefinition(m).Name) == ".cctor"); continue; }
      if (Bad(name)) renamed++;
    }
    foreach (var mh in md.MethodDefinitions) {
      var m = md.GetMethodDefinition(mh); if (m.RelativeVirtualAddress == 0) continue;
      try { var body = pe.GetMethodBody(m.RelativeVirtualAddress); if (!ValidIL(body.GetILBytes())) enc++; } catch { enc++; }
    }
    var F = new Dictionary<string, string> { ["obfuscator"] = obf, ["obfuscator_marker"] = marker,
      ["has_suppress_ildasm"] = sup ? "true" : "false", ["renamed_types"] = renamed.ToString(),
      ["module_cctor"] = mcctor ? "true" : "false", ["encrypted_bodies"] = enc.ToString(),
      ["cctor_decrypts_bodies"] = mcctor && enc > 0 ? "true" : "false" };
    // HCFG via the runtime: module ctor first (the anti-tamper decrypt), then every static byte[] / string field + #US
    object hc = null; int stored = -1;
    var asm = Assembly.LoadFile(Path.GetFullPath(a[0]));
    RuntimeHelpers.RunModuleConstructor(asm.ManifestModule.ModuleHandle);
    foreach (var t in asm.ManifestModule.GetTypes())
      foreach (var f in t.GetFields(BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public))
        if (f.FieldType == typeof(byte[]) && hc == null) {
          var b = (byte[])f.GetValue(null); var j = Hcfg(b, out int at); if (j == null) continue;
          hc = JsonDocument.Parse(j).RootElement;
          // stored offset = the field's FieldRVA data (<PrivateImplementationDetails> initializer) found by SRM
          foreach (var fh in md.FieldDefinitions) { var fd = md.GetFieldDefinition(fh); int rva = fd.GetRelativeVirtualAddress();
            if (rva == 0) continue; pe.PEHeaders.TryGetDirectoryOffset(new DirectoryEntry(rva, 0), out int off);
            if (off + b.Length <= raw.Length) stored = off + at; }
        }
    for (int h = 1; hc == null && h < md.GetHeapSize(HeapIndex.UserString); ) {
      var uh = MetadataTokens.UserStringHandle(h); var s = md.GetUserString(uh);
      try { var b = Convert.FromBase64String(s); var j = Hcfg(b, out int _); if (j != null) { hc = JsonDocument.Parse(j).RootElement;
          var u16 = Encoding.Unicode.GetBytes(s); for (int i = 0; i + u16.Length <= raw.Length; i++) if (raw.AsSpan(i, u16.Length).SequenceEqual(u16)) { stored = i; break; } } } catch { }
      h = MetadataTokens.GetHeapOffset(md.GetNextHandle(uh)); if (h <= 0) break;
    }
    Console.WriteLine(JsonSerializer.Serialize(new { facts = F, hcfg = hc, offset = stored }));
    return 0;
  }
}
