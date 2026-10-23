// Independent reader for the dnlang_* fixtures: System.Reflection.Metadata (BCL ECMA-335 reader, not dnfile).
// Prints the raw metadata facts the language rules use; {"_all":"none"} when not a CLI assembly.
using System; using System.IO; using System.Linq; using System.Text.Json; using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Reflection.Metadata; using System.Reflection.PortableExecutable;
static class O { static void Main(string[] a) {
  var d = new Dictionary<string, object>();
  using var fs = File.OpenRead(a[0]);
  PEReader pe; MetadataReader md;
  try { pe = new PEReader(fs); if (!pe.HasMetadata) throw new Exception(); md = pe.GetMetadataReader(); }
  catch { Console.WriteLine("{\"_all\":\"none\"}"); return; }
  var refs = md.AssemblyReferences.Select(h => md.GetAssemblyReference(h)).ToList();
  string RV(string n) { var r = refs.Where(x => md.GetString(x.Name) == n).ToList(); return r.Count > 0 ? r[0].Version.ToString() : "none"; }
  var an = md.IsAssembly ? md.GetString(md.GetAssemblyDefinition().Name) : "none";
  var av = md.IsAssembly ? md.GetAssemblyDefinition().Version.ToString() : "none";
  d["assembly_name"] = an; d["assembly_version"] = av;
  d["assembly_refs"] = refs.Select(r => md.GetString(r.Name)).ToList();
  d["fsharp_core_version_ref"] = RV("FSharp.Core");
  d["fsharp_core_version_def"] = an == "FSharp.Core" ? av : "none";
  var vb = refs.Select(r => md.GetString(r.Name)).FirstOrDefault(n => n == "Microsoft.VisualBasic" || n == "Microsoft.VisualBasic.Core");
  d["vb_runtime_ref"] = vb ?? "none"; d["vb_runtime_version"] = vb == null ? "none" : RV(vb);
  var res = md.ManifestResources.Select(h => md.GetString(md.GetManifestResource(h).Name)).ToList();
  var fres = res.Where(r => r.StartsWith("FSharpSignature") || r.StartsWith("FSharpOptimization")).ToList();
  d["fsharp_resources"] = fres; d["fsharp_resource_count"] = fres.Count.ToString();
  var tds = md.TypeDefinitions.Select(h => md.GetTypeDefinition(h)).Select(t => (ns: md.GetString(t.Namespace), n: md.GetString(t.Name))).ToList();
  var st = tds.Where(t => t.ns.StartsWith("<StartupCode$")).Select(t => t.ns.Substring(13, t.ns.IndexOf('>') - 13)).Distinct().OrderBy(x => x, StringComparer.Ordinal).ToList();
  d["startup_code"] = st.Count > 0 ? st[0] : "none";
  d["fs_closure_types"] = tds.Count(t => Regex.IsMatch(t.n, "@[0-9]+(-[0-9]+)*$")).ToString();
  d["vb_closure_types"] = tds.Count(t => t.n.StartsWith("_Closure$__")).ToString();
  d["cs_closure_types"] = tds.Count(t => t.n == "<>c" || t.n.StartsWith("<>c__DisplayClass")).ToString();
  d["anon_type_count"] = tds.Count(t => t.n.StartsWith("<>f__AnonymousType") || t.n.StartsWith("VB$AnonymousType_")).ToString();
  d["vb_local_fields"] = md.FieldDefinitions.Count(h => { var n = md.GetString(md.GetFieldDefinition(h).Name); return n.StartsWith("$VB$Local_") || n.StartsWith("$VB$Me") || n.StartsWith("$VB$NonLocal_") || n.StartsWith("$VB$ResumableLocal_"); }).ToString();
  d["il_only"] = (pe.PEHeaders.CorHeader.Flags & CorFlags.ILOnly) != 0 ? "true" : "false";
  d["machine"] = pe.PEHeaders.CoffHeader.Machine.ToString();
  Console.WriteLine(JsonSerializer.Serialize(d));
} }
