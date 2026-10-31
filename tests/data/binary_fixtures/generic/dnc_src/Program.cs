// dnc_cs fixture: every TypeDef kind the gf-dotnet-counts rule classifies (nested, compiler-generated, interface, enum,
// struct, delegate, generic, attribute, exception) plus #US user strings.
using System; using System.Collections.Generic;
namespace Acme.Tools {
  public interface IPlugin { string Name { get; } }
  public enum Mode { Idle, Beacon, Exfil }
  public struct Point { public int X; public int Y; }
  public delegate void Handler(string s);
  public sealed class MarkerAttribute : Attribute { }
  public class StageException : Exception { public StageException(string m) : base(m) { } }
  public class Box<T> { public T Value; }
  public static class Util { public static readonly byte[] Key = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 };
    public static int Twice(int v) => v * 2; }
  public class Outer { public class Inner { public int Depth = 2; } private class Hidden { } }
  [Marker] public class Program : IPlugin {
    public string Name { get; set; } = "acme-loader";
    static IEnumerable<int> Gen() { yield return 1; yield return 2; }
    public static int Main(string[] args) {
      var p = new Program(); Func<int, int> f = x => x + 1; int s = 0;
      foreach (var g in Gen()) s += f(g);
      Console.WriteLine("http://cfg.example.invalid/beacon"); Console.WriteLine("MUTEX-ACME-7");
      Console.WriteLine(p.Name + Mode.Beacon + Util.Twice(s) + Util.Key.Length);
      return 0; } }
}
