// Independent reader for the dnmeta_* fixtures: System.Reflection.Metadata (the BCL's own ECMA-335 reader, not dnfile).
// usage: bash dnmeta_oracle.sh <file>  -> one JSON object of facts (table order, names as stored), or {"_all":"none"}.
using System; using System.IO; using System.Linq; using System.Text.Json; using System.Collections.Generic;
using System.Reflection.Metadata; using System.Reflection.Metadata.Ecma335; using System.Reflection.PortableExecutable;
static class O { static void Main(string[] a) {
  var d = new Dictionary<string, string>();
  using var fs = File.OpenRead(a[0]);
  PEReader pe; MetadataReader md;
  try { pe = new PEReader(fs); if (!pe.HasMetadata) throw new Exception(); md = pe.GetMetadataReader(); }
  catch { Console.WriteLine("{\"_all\":\"none\"}"); return; }
  var jo = new JsonSerializerOptions { Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping };
  string J(IEnumerable<string> x) => JsonSerializer.Serialize(x.ToList(), jo);
  if (md.IsAssembly) { var ad = md.GetAssemblyDefinition(); d["assembly_name"] = md.GetString(ad.Name);
    d["assembly_version"] = ad.Version.ToString(); d["assembly_culture"] = ad.Culture.IsNil ? "none" : md.GetString(ad.Culture);
    if (d["assembly_culture"] == "") d["assembly_culture"] = "none"; }
  else { d["assembly_name"] = "none"; d["assembly_version"] = "none"; }
  var mod = md.GetModuleDefinition(); d["module_name"] = md.GetString(mod.Name);
  d["mvid"] = md.GetGuid(mod.Mvid).ToString();
  d["runtime_version"] = md.MetadataVersion;
  var tds = md.TypeDefinitions.Select(h => md.GetTypeDefinition(h)).ToList();
  d["typedefs"] = J(tds.Select(t => md.GetString(t.Name)));
  d["typedefs_full"] = J(tds.Select(t => { var ns = md.GetString(t.Namespace); return ns == "" ? md.GetString(t.Name) : ns + "." + md.GetString(t.Name); }));
  d["typedef_count"] = tds.Count.ToString();
  var ms = md.MethodDefinitions.Select(h => md.GetMethodDefinition(h)).ToList();
  d["methods"] = J(ms.Select(m => md.GetString(m.Name))); d["method_count"] = ms.Count.ToString();
  var fl = md.FieldDefinitions.Select(h => md.GetFieldDefinition(h)).ToList();
  d["fields"] = J(fl.Select(f => md.GetString(f.Name))); d["field_count"] = fl.Count.ToString();
  int rvas = fl.Count(f => f.GetRelativeVirtualAddress() != 0);
  d["field_rva_count"] = rvas.ToString(); d["has_field_rva"] = rvas > 0 ? "true" : "false";
  int ep = pe.PEHeaders.CorHeader.EntryPointTokenOrRelativeVirtualAddress;
  d["entry_point_token"] = ep == 0 ? "none" : "0x" + ep.ToString("x8");
  if (ep != 0 && (ep >> 24) == 6) { var m = md.GetMethodDefinition(MetadataTokens.MethodDefinitionHandle(ep & 0xffffff));
    var t = md.GetTypeDefinition(m.GetDeclaringType()); var ns = md.GetString(t.Namespace);
    d["entry_point"] = (ns == "" ? "" : ns + ".") + md.GetString(t.Name) + "." + md.GetString(m.Name); } else d["entry_point"] = "none";
  d["target_framework"] = "none";
  foreach (var ch in md.GetAssemblyDefinition().GetCustomAttributes()) { var ca = md.GetCustomAttribute(ch);
    if (ca.Constructor.Kind != HandleKind.MemberReference) continue; var mr = md.GetMemberReference((MemberReferenceHandle)ca.Constructor);
    if (mr.Parent.Kind != HandleKind.TypeReference || md.GetString(md.GetTypeReference((TypeReferenceHandle)mr.Parent).Name) != "TargetFrameworkAttribute") continue;
    var br = md.GetBlobReader(ca.Value); br.ReadUInt16(); d["target_framework"] = br.ReadSerializedString(); }
  d["assembly_refs"] = J(md.AssemblyReferences.Select(h => md.GetString(md.GetAssemblyReference(h).Name)));
  var us = new List<string>(); var uh = MetadataTokens.UserStringHandle(1);
  while (!uh.IsNil) { var s = md.GetUserString(uh); if (s.Length > 0) us.Add(s); uh = md.GetNextHandle(uh); }
  d["user_strings"] = J(us);
  Console.WriteLine(JsonSerializer.Serialize(d, jo));
} }
