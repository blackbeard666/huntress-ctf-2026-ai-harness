// Independent reader for the cominterop_* fixtures: System.Reflection.Metadata (the BCL's ECMA-335 reader, not dnfile).
// usage: bash cominterop_oracle.sh <file> -> one JSON object of COM-interop facts, or {"_all":"none"}.
using System; using System.IO; using System.Linq; using System.Text.Json; using System.Collections.Generic;
using System.Reflection; using System.Reflection.Metadata; using System.Reflection.Metadata.Ecma335; using System.Reflection.PortableExecutable;
static class O { static void Main(string[] a) {
  var d = new Dictionary<string, string>();
  using var fs = File.OpenRead(a[0]); PEReader pe; MetadataReader md;
  try { pe = new PEReader(fs); if (!pe.HasMetadata) throw new Exception(); md = pe.GetMetadataReader(); }
  catch { Console.WriteLine("{\"_all\":\"none\"}"); return; }
  var jo = new JsonSerializerOptions { Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping };
  string J<T>(IEnumerable<T> x) => JsonSerializer.Serialize(x.ToList(), jo);
  string AttrName(CustomAttribute ca) {
    EntityHandle p = ca.Constructor.Kind == HandleKind.MemberReference ? md.GetMemberReference((MemberReferenceHandle)ca.Constructor).Parent
                   : md.GetMethodDefinition((MethodDefinitionHandle)ca.Constructor).GetDeclaringType();
    return p.Kind == HandleKind.TypeReference ? md.GetString(md.GetTypeReference((TypeReferenceHandle)p).Name)
         : p.Kind == HandleKind.TypeDefinition ? md.GetString(md.GetTypeDefinition((TypeDefinitionHandle)p).Name) : ""; }
  BlobReader? Find(CustomAttributeHandleCollection c, string n) { foreach (var h in c) { var ca = md.GetCustomAttribute(h);
      if (AttrName(ca) == n) { var br = md.GetBlobReader(ca.Value); br.ReadUInt16(); return br; } } return null; }
  string G(string s) => Guid.Parse(s).ToString("D");
  string asmGuid = "none"; var b0 = Find(md.GetAssemblyDefinition().GetCustomAttributes(), "GuidAttribute");
  if (b0 is BlobReader ab) asmGuid = G(ab.ReadSerializedString());
  var ifs = new List<string>(); var iids = new List<string>(); var cls = new List<string>(); var clsids = new List<string>();
  var props = new Dictionary<MethodDefinitionHandle, PropertyDefinitionHandle>();
  foreach (var th in md.TypeDefinitions) { var t = md.GetTypeDefinition(th);
    foreach (var ph in t.GetProperties()) { var acc = md.GetPropertyDefinition(ph).GetAccessors();
      if (!acc.Getter.IsNil) props[acc.Getter] = ph; if (!acc.Setter.IsNil) props[acc.Setter] = ph; } }
  bool any = false;
  foreach (var th in md.TypeDefinitions) { var t = md.GetTypeDefinition(th); var n = md.GetString(t.Name);
    bool imp = (t.Attributes & TypeAttributes.Import) != 0, isif = (t.Attributes & TypeAttributes.Interface) != 0;
    bool gen = Find(t.GetCustomAttributes(), "GeneratedComInterfaceAttribute") != null;
    var gb = Find(t.GetCustomAttributes(), "GuidAttribute"); string g = gb is BlobReader gr ? G(gr.ReadSerializedString()) : "none";
    if (!(imp || gen || (gb != null && !isif))) continue; any = true;
    d[n + "_guid"] = g; d[n + "_guid_upper"] = g == "none" ? "none" : g.ToUpperInvariant();
    if (!isif) { if (imp) { cls.Add(n); clsids.Add(g); } d[n + "_clsid"] = g;
      var pb = Find(t.GetCustomAttributes(), "ProgIdAttribute"); d[n + "_progid"] = pb is BlobReader pr ? pr.ReadSerializedString() : "none"; continue; }
    ifs.Add(n); iids.Add(g); d[n + "_iid"] = g;
    string it = "dual"; var ib = Find(t.GetCustomAttributes(), "InterfaceTypeAttribute");
    if (gen) it = "iunknown"; else if (ib is BlobReader ir) { int v = ir.Length - ir.Offset >= 6 ? ir.ReadInt32() : ir.ReadInt16();
      it = new[] { "dual", "iunknown", "idispatch", "iinspectable" }[v]; }
    int bas = it == "iunknown" ? 3 : it == "iinspectable" ? 6 : 7;
    d[n + "_interface_type"] = it; d[n + "_vtable_base"] = bas.ToString();
    var cb = Find(t.GetCustomAttributes(), "CoClassAttribute"); d[n + "_coclass"] = cb is BlobReader cr ? cr.ReadSerializedString().Split('.').Last() : "none";
    var names = new List<string>(); int i = 0; var slots = new Dictionary<string, int>();
    foreach (var mh in t.GetMethods()) { var m = md.GetMethodDefinition(mh); var mn = md.GetString(m.Name); names.Add(mn); slots[mn] = i + bas;
      d[$"{n}_{mn}_vtable_slot"] = (i + bas).ToString(); d[$"{n}_{mn}_vtable_offset"] = "0x" + ((i + bas) * 8).ToString("x");
      var db = Find(m.GetCustomAttributes(), "DispIdAttribute");
      if (db == null && props.TryGetValue(mh, out var ph)) db = Find(md.GetPropertyDefinition(ph).GetCustomAttributes(), "DispIdAttribute");
      d[$"{n}_{mn}_dispid"] = db is BlobReader dr ? dr.ReadInt32().ToString() : "none"; i++; }
    d[n + "_methods"] = J(names); d[n + "_method_count"] = names.Count.ToString(); d[n + "_vtable_slots"] = JsonSerializer.Serialize(slots); }
  if (!any) { Console.WriteLine("{\"_all\":\"none\"}"); return; }
  d["com_interfaces"] = J(ifs); d["com_iids"] = J(iids); d["com_interface_count"] = ifs.Count.ToString();
  d["com_classes"] = J(cls); d["com_clsids"] = J(clsids); d["assembly_guid"] = asmGuid;
  var pinv = new List<string>();
  foreach (var mh in md.MethodDefinitions) { var imp = md.GetMethodDefinition(mh).GetImport(); if (imp.Module.IsNil) continue;
    var mod = md.GetString(md.GetModuleReference(imp.Module).Name); var e = md.GetString(imp.Name);
    if (new[] { "ole32", "oleaut32", "combase" }.Contains(mod.ToLowerInvariant().Replace(".dll", "")) || e.StartsWith("Co")) pinv.Add(mod + "!" + e); }
  d["com_pinvokes"] = J(pinv);
  var gs = new List<string>(); var h = MetadataTokens.UserStringHandle(1);
  while (!h.IsNil) { var s = md.GetUserString(h); if (Guid.TryParseExact(s.Trim('{', '}'), "D", out var gg) && !gs.Contains(gg.ToString())) gs.Add(gg.ToString()); h = md.GetNextHandle(h); }
  d["guid_strings"] = J(gs);
  var progs = new List<string>();
  foreach (var th in md.TypeDefinitions) { var pb = Find(md.GetTypeDefinition(th).GetCustomAttributes(), "ProgIdAttribute"); if (pb is BlobReader pr) progs.Add(pr.ReadSerializedString()); }
  foreach (var mh in md.MethodDefinitions) { var m = md.GetMethodDefinition(mh); if (m.RelativeVirtualAddress == 0) continue;
    var il = pe.GetMethodBody(m.RelativeVirtualAddress).GetILReader(); string last = null;
    while (il.RemainingBytes > 0) { int op = il.ReadByte(); if (op == 0xFE) { il.ReadByte(); continue; }   // no 2-byte ops w/ operands here
      if (op == 0x72) { last = md.GetUserString((UserStringHandle)MetadataTokens.Handle(il.ReadInt32())); continue; }
      if (op == 0x28 || op == 0x6F || op == 0x73) { var tok = MetadataTokens.EntityHandle(il.ReadInt32());
        if (tok.Kind == HandleKind.MemberReference && md.GetString(md.GetMemberReference((MemberReferenceHandle)tok).Name) == "GetTypeFromProgID" && last != null) progs.Add(last);
        last = null; continue; }
      int sz = op switch { 0x20 or 0x22 or (>= 0x38 and <= 0x44) or 0xDD or 0x27 or 0x29 or 0x70 or 0x71 or 0x74 or 0x75 or 0x79 or (>= 0x7B and <= 0x81) or 0x8C or 0x8D or 0x8F or 0xA5 or 0xC2 or 0xC6 or 0xD0 => 4,
                           0x21 or 0x23 => 8, (>= 0x0E and <= 0x13) or 0x1F or (>= 0x2B and <= 0x37) or 0xDE => 1, _ => 0 };
      if (op == 0x45) sz = 4 * il.ReadInt32(); for (int k = 0; k < sz; k++) il.ReadByte(); if (op != 0x0A && !(op >= 0x02 && op <= 0x13)) last = null; } }
  d["com_progids"] = J(progs.Distinct());
  Console.WriteLine(JsonSerializer.Serialize(d, jo)); } }
