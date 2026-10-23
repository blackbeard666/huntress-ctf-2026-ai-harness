// #US heap oracle: System.Reflection.Metadata MetadataReader.UserStrings in heap order -> JSON array of strings
using System; using System.IO; using System.Linq; using System.Reflection.Metadata; using System.Reflection.Metadata.Ecma335; using System.Reflection.PortableExecutable;
using System.Text.Json;
class U { static void Main(string[] a) {
  using var pe = new PEReader(File.OpenRead(a[0])); var md = pe.GetMetadataReader();
  var list = new System.Collections.Generic.List<string>();
  var h = MetadataTokens.UserStringHandle(1);
  while (!h.IsNil && MetadataTokens.GetHeapOffset(h) < md.GetHeapSize(HeapIndex.UserString)) {
    var s = md.GetUserString(h); var nx = md.GetNextHandle(h);
    // an entry of 1 byte is a 0x00 length (heap alignment padding), not a string; a real "" takes 2 bytes
    int end = nx.IsNil ? md.GetHeapSize(HeapIndex.UserString) : MetadataTokens.GetHeapOffset(nx);
    if (end - MetadataTokens.GetHeapOffset(h) > 1) list.Add(s); h = nx; }
  Console.WriteLine(JsonSerializer.Serialize(list, new JsonSerializerOptions { Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping }));
} }
