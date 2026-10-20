Add-Type -TypeDefinition @'
public static class W { public static int Add(int a, int b) { return a + b; } }
'@
[W]::Add(1, 2)
