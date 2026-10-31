// Independent reader for the gf-dotnet-counts fixtures: System.Reflection.Metadata (the BCL ECMA-335 reader, not dnfile).
// usage: bash dnc_oracle.sh FILE -> one JSON object (counts, name lists, kind flags) or {"_all":"none"}.
using System; using System.IO; using System.Linq; using System.Text.Json; using System.Collections.Generic;
using System.Reflection; using System.Reflection.Metadata; using System.Reflection.Metadata.Ecma335;
using System.Reflection.PortableExecutable;
static class O { static void Main(string[] a) {
  using var fs = File.OpenRead(a[0]); PEReader pe; MetadataReader md;
  try { pe = new PEReader(fs); if (!pe.HasMetadata) throw new Exception(); md = pe.GetMetadataReader(); }
  catch { Console.WriteLine("{\"_all\":\"none\"}"); return; }
  var d = new Dictionary<string, object>();
  var hs = md.TypeDefinitions.ToList(); var first = hs[0];
  string Base(TypeDefinition t) { var b = t.BaseType; if (b.IsNil) return "";
    if (b.Kind == HandleKind.TypeReference) { var r = md.GetTypeReference((TypeReferenceHandle)b); return md.GetString(r.Namespace) + "." + md.GetString(r.Name); }
    if (b.Kind == HandleKind.TypeDefinition) { var r = md.GetTypeDefinition((TypeDefinitionHandle)b); var ns = md.GetString(r.Namespace); return (ns == "" ? "" : ns + ".") + md.GetString(r.Name); }
    return "?"; }
  bool CgAttr(TypeDefinition t) => t.GetCustomAttributes().Select(h => md.GetCustomAttribute(h)).Any(c => c.Constructor.Kind == HandleKind.MemberReference &&
      md.GetMemberReference((MemberReferenceHandle)c.Constructor).Parent is var p && p.Kind == HandleKind.TypeReference &&
      md.GetString(md.GetTypeReference((TypeReferenceHandle)p).Name) == "CompilerGeneratedAttribute");
  bool Cg(TypeDefinitionHandle h) { if (h == first) return false; var t = md.GetTypeDefinition(h);
    if (CgAttr(t) || md.GetString(t.Name).StartsWith("<") || md.GetString(t.Namespace).StartsWith("<")) return true;
    var e = t.GetDeclaringType(); return !e.IsNil && Cg(e); }
  var T = hs.Select(h => (h, t: md.GetTypeDefinition(h))).ToList();
  bool Nested(TypeDefinition t) => !t.GetDeclaringType().IsNil;
  d["typedef_count"] = T.Count; d["typedef_count_nomodule"] = T.Count - 1;
  d["compiler_generated_type_count"] = T.Count(x => Cg(x.h));
  d["user_type_count"] = T.Count(x => x.h != first && !Cg(x.h));
  d["nested_type_count"] = T.Count(x => Nested(x.t));
  d["top_level_type_count"] = T.Count(x => x.h != first && !Nested(x.t));
  d["interface_count"] = T.Count(x => (x.t.Attributes & TypeAttributes.Interface) != 0);
  d["enum_count"] = T.Count(x => Base(x.t) == "System.Enum");
  d["struct_count"] = T.Count(x => Base(x.t) == "System.ValueType");
  d["delegate_count"] = T.Count(x => Base(x.t) == "System.MulticastDelegate");
  d["type_names"] = T.Select(x => md.GetString(x.t.Name)).ToList();
  d["user_type_full_names"] = T.Where(x => x.h != first && !Cg(x.h)).Select(x => { var ns = md.GetString(x.t.Namespace); return (ns == "" ? "" : ns + ".") + md.GetString(x.t.Name); }).ToList();
  var ms = md.MethodDefinitions.Select(h => md.GetString(md.GetMethodDefinition(h).Name)).ToList();
  d["method_count"] = ms.Count; d["method_count_noctor"] = ms.Count(n => n != ".ctor" && n != ".cctor"); d["method_names"] = ms;
  var fl = md.FieldDefinitions.Select(h => md.GetString(md.GetFieldDefinition(h).Name)).ToList();
  d["field_count"] = fl.Count; d["field_names"] = fl;
  var us = new List<string>(); var u = MetadataTokens.UserStringHandle(1);
  if (md.GetHeapSize(HeapIndex.UserString) > 1) while (!u.IsNil) { var s = md.GetUserString(u); if (s.Length > 0) us.Add(s); u = md.GetNextHandle(u); }
  d["user_strings"] = us; d["user_string_count"] = us.Count;
  d["assembly_ref_count"] = md.AssemblyReferences.Count;
  var jo = new JsonSerializerOptions { Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping };
  Console.WriteLine(JsonSerializer.Serialize(d, jo)); } }
