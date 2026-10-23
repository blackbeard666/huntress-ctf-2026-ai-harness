// Independent reader for the pinv_* fixtures: System.Reflection.Metadata (the BCL's ECMA-335 reader, not dnfile) +
// System.Reflection.Emit.OpCodes for a full IL walk. usage: bash pinv_oracle.sh <file> -> one JSON object, or {"_all":"none"}.
using System; using System.IO; using System.Linq; using System.Text.Json; using System.Collections.Generic;
using System.Collections.Immutable; using System.Reflection; using System.Reflection.Emit;
using System.Reflection.Metadata; using System.Reflection.Metadata.Ecma335; using System.Reflection.PortableExecutable;
using T2 = System.ValueTuple<string, string>;
sealed class Prov : ISignatureTypeProvider<T2, object>, ICustomAttributeTypeProvider<string> {
  public T2 GetPrimitiveType(PrimitiveTypeCode c) => c switch {
    PrimitiveTypeCode.Void => ("void", "void"), PrimitiveTypeCode.Boolean => ("bool", "bool"), PrimitiveTypeCode.Char => ("char", "char"),
    PrimitiveTypeCode.SByte => ("sbyte", "int8"), PrimitiveTypeCode.Byte => ("byte", "uint8"), PrimitiveTypeCode.Int16 => ("short", "int16"),
    PrimitiveTypeCode.UInt16 => ("ushort", "uint16"), PrimitiveTypeCode.Int32 => ("int", "int32"), PrimitiveTypeCode.UInt32 => ("uint", "uint32"),
    PrimitiveTypeCode.Int64 => ("long", "int64"), PrimitiveTypeCode.UInt64 => ("ulong", "uint64"), PrimitiveTypeCode.Single => ("float", "float32"),
    PrimitiveTypeCode.Double => ("double", "float64"), PrimitiveTypeCode.String => ("string", "string"),
    PrimitiveTypeCode.IntPtr => ("IntPtr", "native int"), PrimitiveTypeCode.UIntPtr => ("UIntPtr", "native uint"),
    PrimitiveTypeCode.Object => ("object", "object"), PrimitiveTypeCode.TypedReference => ("TypedReference", "typedref"), _ => ("?", "?") };
  public MetadataReader R;
  public T2 GetTypeFromDefinition(MetadataReader r, TypeDefinitionHandle h, byte k) { var n = r.GetString(r.GetTypeDefinition(h).Name); return (n, n); }
  public T2 GetTypeFromReference(MetadataReader r, TypeReferenceHandle h, byte k) { var n = r.GetString(r.GetTypeReference(h).Name); return (n, n); }
  public T2 GetTypeFromSpecification(MetadataReader r, object g, TypeSpecificationHandle h, byte k) => ("?", "?");
  public T2 GetPointerType(T2 e) => (e.Item1 + "*", e.Item2 + "*");
  public T2 GetByReferenceType(T2 e) => ("ref " + e.Item1, e.Item2 + "&");
  public T2 GetSZArrayType(T2 e) => (e.Item1 + "[]", e.Item2 + "[]");
  public T2 GetArrayType(T2 e, ArrayShape s) { var x = "[" + new string(',', Math.Max(s.Rank - 1, 0)) + "]"; return (e.Item1 + x, e.Item2 + x); }
  public T2 GetPinnedType(T2 e) => e; public T2 GetModifiedType(T2 m, T2 u, bool req) => u;
  public T2 GetGenericInstantiation(T2 g, ImmutableArray<T2> a) => (g.Item1.Split('`')[0] + "<" + string.Join(",", a.Select(x => x.Item1)) + ">", g.Item2.Split('`')[0] + "<" + string.Join(",", a.Select(x => x.Item2)) + ">");
  public T2 GetGenericTypeParameter(object g, int i) => ("T" + i, "!" + i); public T2 GetGenericMethodParameter(object g, int i) => ("T" + i, "!!" + i);
  public T2 GetFunctionPointerType(MethodSignature<T2> s) => ("delegate*", "method");
  // ICustomAttributeTypeProvider<string>
  string ISimpleTypeProvider<string>.GetPrimitiveType(PrimitiveTypeCode c) => c.ToString();
  string ISimpleTypeProvider<string>.GetTypeFromDefinition(MetadataReader r, TypeDefinitionHandle h, byte k) => "td";
  string ISimpleTypeProvider<string>.GetTypeFromReference(MetadataReader r, TypeReferenceHandle h, byte k) => "tr";
  public string GetSZArrayType(string e) => e + "[]"; public string GetSystemType() => "Type";
  public string GetTypeFromSerializedName(string n) => n; public PrimitiveTypeCode GetUnderlyingEnumType(string t) => PrimitiveTypeCode.Int32;
  public bool IsSystemType(string t) => t == "Type";
}
static class O {
  static Dictionary<short, OpCode> ops = typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static).Select(f => (OpCode)f.GetValue(null)).ToDictionary(o => o.Value);
  static void Main(string[] a) {
    var d = new Dictionary<string, object>();
    using var fs = File.OpenRead(a[0]);
    PEReader pe; MetadataReader md;
    try { pe = new PEReader(fs); if (!pe.HasMetadata) throw new Exception(); md = pe.GetMetadataReader(); }
    catch { Console.WriteLine("{\"_all\":\"none\"}"); return; }
    var jo = new JsonSerializerOptions { Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping };
    string J(object x) => JsonSerializer.Serialize(x, jo);
    var pv = new Prov { R = md };
    var mods = md.GetTableRowCount(TableIndex.ModuleRef);
    var modNames = Enumerable.Range(1, mods).Select(i => md.GetString(md.GetModuleReference(MetadataTokens.ModuleReferenceHandle(i)).Name)).ToList();
    d["native_modules"] = J(modNames); d["native_module_count"] = mods.ToString();
    var det = new List<Dictionary<string, object>>(); var imps = new List<Dictionary<string, string>>();
    string Tri(bool en, bool dis) => en ? "true" : dis ? "false" : "default";
    foreach (var mh in md.MethodDefinitions) { var m = md.GetMethodDefinition(mh);
      if ((m.Attributes & MethodAttributes.PinvokeImpl) == 0) continue;
      var im = m.GetImport(); var A = im.Attributes; string name = md.GetString(m.Name), entry = md.GetString(im.Name);
      if (entry == "") entry = name;
      var t = md.GetTypeDefinition(m.GetDeclaringType()); var ns = md.GetString(t.Namespace);
      var cc = (A & MethodImportAttributes.CallingConventionMask) switch { MethodImportAttributes.CallingConventionWinApi => "winapi",
        MethodImportAttributes.CallingConventionCDecl => "cdecl", MethodImportAttributes.CallingConventionStdCall => "stdcall",
        MethodImportAttributes.CallingConventionThisCall => "thiscall", MethodImportAttributes.CallingConventionFastCall => "fastcall", _ => "none" };
      var cs = (A & MethodImportAttributes.CharSetMask) switch { MethodImportAttributes.CharSetAnsi => "ansi", MethodImportAttributes.CharSetUnicode => "unicode", MethodImportAttributes.CharSetAuto => "auto", _ => "none" };
      var sig = m.DecodeSignature(pv, null);
      var pn = new string[sig.ParameterTypes.Length]; var pm = Enumerable.Repeat("none", pn.Length).ToArray(); string rm = "none";
      for (int i = 0; i < pn.Length; i++) pn[i] = "arg" + i;
      foreach (var ph in m.GetParameters()) { var p = md.GetParameter(ph); var mb = p.GetMarshallingDescriptor();
        string mk = mb.IsNil ? "none" : ((System.Runtime.InteropServices.UnmanagedType)md.GetBlobBytes(mb)[0]).ToString();
        if (p.SequenceNumber == 0) rm = mk; else if (p.SequenceNumber <= pn.Length) { pn[p.SequenceNumber - 1] = md.GetString(p.Name); pm[p.SequenceNumber - 1] = mk; } }
      var e = new Dictionary<string, object> { ["method"] = name, ["entry"] = entry, ["module"] = modNames[MetadataTokens.GetRowNumber(im.Module) - 1],
        ["type"] = (ns == "" ? "" : ns + ".") + md.GetString(t.Name), ["token"] = "0x" + MetadataTokens.GetToken(mh).ToString("x8"),
        ["callconv"] = cc, ["charset"] = cs, ["set_last_error"] = (A & MethodImportAttributes.SetLastError) != 0 ? "true" : "false",
        ["exact_spelling"] = (A & MethodImportAttributes.ExactSpelling) != 0 ? "true" : "false",
        ["best_fit"] = Tri((A & MethodImportAttributes.BestFitMappingMask) == MethodImportAttributes.BestFitMappingEnable, (A & MethodImportAttributes.BestFitMappingMask) == MethodImportAttributes.BestFitMappingDisable),
        ["throw_on_unmappable"] = Tri((A & MethodImportAttributes.ThrowOnUnmappableCharMask) == MethodImportAttributes.ThrowOnUnmappableCharEnable, (A & MethodImportAttributes.ThrowOnUnmappableCharMask) == MethodImportAttributes.ThrowOnUnmappableCharDisable),
        ["preserve_sig"] = (m.ImplAttributes & MethodImplAttributes.PreserveSig) != 0 ? "true" : "false", ["flags"] = "0x" + ((int)A).ToString("x4"),
        ["return"] = sig.ReturnType.Item1, ["params"] = sig.ParameterTypes.Select(x => x.Item1).ToList(),
        ["return_il"] = sig.ReturnType.Item2, ["params_il"] = sig.ParameterTypes.Select(x => x.Item2).ToList(), ["param_names"] = pn.ToList(),
        ["return_marshal"] = rm, ["param_marshal"] = pm.ToList(),
        ["signature"] = sig.ReturnType.Item1 + " " + name + "(" + string.Join(", ", sig.ParameterTypes.Select((x, i) => x.Item1 + " " + pn[i])) + ")" };
      det.Add(e); imps.Add(new Dictionary<string, string> { ["method"] = name, ["entry"] = entry, ["module"] = (string)e["module"] }); }
    d["pinvoke_count"] = det.Count.ToString(); d["pinvoke_methods"] = J(det.Select(x => x["method"])); d["pinvoke_entries"] = J(det.Select(x => x["entry"]));
    d["pinvoke_imports"] = J(imps); d["pinvoke_details"] = J(det); d["pinvoke_modules"] = J(det.Select(x => (string)x["module"]).Distinct());
    d["set_last_error_methods"] = J(det.Where(x => (string)x["set_last_error"] == "true").Select(x => x["method"]));
    var li = new List<string>(); var uco = new List<string>(); var ucoE = new List<string>();
    foreach (var mh in md.MethodDefinitions) { var m = md.GetMethodDefinition(mh);
      foreach (var ch in m.GetCustomAttributes()) { var ca = md.GetCustomAttribute(ch); string an = null;
        if (ca.Constructor.Kind == HandleKind.MemberReference) { var mr = md.GetMemberReference((MemberReferenceHandle)ca.Constructor);
          if (mr.Parent.Kind == HandleKind.TypeReference) an = md.GetString(md.GetTypeReference((TypeReferenceHandle)mr.Parent).Name); }
        if (an == "LibraryImportAttribute") li.Add(md.GetString(m.Name));
        if (an == "UnmanagedCallersOnlyAttribute") { uco.Add(md.GetString(m.Name));
          var v = ca.DecodeValue(pv); foreach (var na in v.NamedArguments) if (na.Name == "EntryPoint" && na.Value is string s) ucoE.Add(s); } } }
    d["library_import_methods"] = J(li); d["library_import_count"] = li.Count.ToString();
    d["unmanaged_callers_only"] = J(uco); d["unmanaged_callers_only_entries"] = J(ucoE);
    var ccs = new List<string>();
    for (int i = 1; i <= md.GetTableRowCount(TableIndex.StandAloneSig); i++) { var ss = md.GetStandaloneSignature(MetadataTokens.StandaloneSignatureHandle(i));
      if (ss.GetKind() != StandaloneSignatureKind.Method) continue; var h = md.GetBlobReader(ss.Signature).ReadSignatureHeader();
      var k = h.CallingConvention switch { SignatureCallingConvention.CDecl => "cdecl", SignatureCallingConvention.StdCall => "stdcall",
        SignatureCallingConvention.ThisCall => "thiscall", SignatureCallingConvention.FastCall => "fastcall", SignatureCallingConvention.Unmanaged => "unmanaged", _ => null };
      if (k != null) ccs.Add(k); }
    d["unmanaged_fnptr_count"] = ccs.Count.ToString(); d["unmanaged_fnptr_callconvs"] = J(ccs.Distinct());
    var want = new HashSet<string> { "NativeLibrary.Load", "NativeLibrary.TryLoad", "NativeLibrary.GetExport", "NativeLibrary.TryGetExport", "NativeLibrary.Free",
      "NativeLibrary.GetMainProgramHandle", "NativeLibrary.SetDllImportResolver", "Marshal.GetDelegateForFunctionPointer", "Marshal.GetFunctionPointerForDelegate" };
    var apis = new Dictionary<int, string>();
    foreach (var h in md.MemberReferences) { var mr = md.GetMemberReference(h); if (mr.Parent.Kind != HandleKind.TypeReference) continue;
      var s = md.GetString(md.GetTypeReference((TypeReferenceHandle)mr.Parent).Name) + "." + md.GetString(mr.Name);
      if (want.Contains(s)) apis[MetadataTokens.GetToken(h)] = s; }
    d["native_library_apis"] = J(apis.Values.Distinct());
    var strs = new List<string>();
    foreach (var mh in md.MethodDefinitions) { var m = md.GetMethodDefinition(mh); if (m.RelativeVirtualAddress == 0) continue;
      var il = pe.GetMethodBody(m.RelativeVirtualAddress).GetILReader(); string last = null; int since = 99;
      while (il.RemainingBytes > 0) { short v = il.ReadByte(); if (v == 0xFE) v = (short)(0xFE00 | il.ReadByte());
        var op = ops[v]; int arg = 0;
        switch (op.OperandType) { case OperandType.InlineNone: break; case OperandType.ShortInlineBrTarget: case OperandType.ShortInlineI: case OperandType.ShortInlineVar: il.ReadByte(); break;
          case OperandType.InlineVar: il.ReadInt16(); break; case OperandType.InlineI8: case OperandType.InlineR: il.ReadInt64(); break;
          case OperandType.InlineSwitch: { int n = il.ReadInt32(); for (int i = 0; i < n; i++) il.ReadInt32(); break; }
          default: arg = il.ReadInt32(); break; }
        if (op == OpCodes.Ldstr) { last = md.GetUserString(MetadataTokens.UserStringHandle(arg & 0xFFFFFF)); since = 0; continue; }
        if (op == OpCodes.Call && apis.ContainsKey(arg) && since <= 1 && last != null) strs.Add(last);
        since++; } }
    d["native_library_strings"] = J(strs);
    foreach (var e in det) foreach (var key in new[] { (string)e["method"], (string)e["entry"] }) foreach (var kv in e) {
      if (kv.Key == "method") continue; var k = key + "_" + kv.Key; if (!d.ContainsKey(k)) d[k] = kv.Value is string s ? s : J(kv.Value); }
    Console.WriteLine(JsonSerializer.Serialize(d.ToDictionary(x => x.Key, x => x.Value.ToString()), jo));
  }
}
