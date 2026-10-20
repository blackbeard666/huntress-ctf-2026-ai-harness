Add-Type -TypeDefinition 'public class HuntressGate { public static string Answer() { return "ANS-3f9c1a7be04d2c58"; } }' -OutputAssembly gate.dll -OutputType Library
Add-Type -TypeDefinition 'public class HuntressGate2 { public static string Answer() { return "ANS-a1b2c3d4e5f60718"; } }' -OutputAssembly gate2.dll -OutputType Library
Add-Type -TypeDefinition 'public class Decoy { public static string Answer() { return "ANS-3f9c1a7be04d2cZZ"; } }' -OutputAssembly decoy.dll -OutputType Library
Add-Type -TypeDefinition 'public class Util { public static string Hello() { return "hello from a helper assembly"; } }' -OutputAssembly util.dll -OutputType Library
