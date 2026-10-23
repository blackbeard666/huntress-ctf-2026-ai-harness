#!/bin/bash
# Runtime-codegen fixtures (lib.binary.runtime_codegen_field). usage: bash rcg_gen.sh OUTDIR   (gcc + dotnet 10 SDK, offline)
#  rcg_elf_rwx_O0.bin     : gcc -O0: mmap(PROT_READ|WRITE|EXEC) + memcpy of `b8 39 05 00 00 c3` (mov eax,1337; ret) -> call
#  rcg_elf_mprotect_O2.bin: gcc -O2 -s: mmap(RW) + memcpy of an 11-byte prologue/mov eax,0x0badbeef/ret array, mprotect(R|X)
#  rcg_decoy_elf_rw.bin   : gcc -O2: same opcode bytes copied into an RW mapping, never made executable -> "false"
#  rcg_cs_dynmethod.bin   : C# DynamicMethod + ILGenerator.Emit(OpCodes.Ldc_I4, 0x1337); Emit(OpCodes.Ret)
#  rcg_cs_asmbuilder.bin  : C# AssemblyBuilder/TypeBuilder/MethodBuilder: Ldc_I8 0x1122334455667788; Ret
#  rcg_cs_expr.bin        : C# Expression.Lambda<Func<int>>(Expression.Constant(424242)).Compile()
#  rcg_decoy_cs_plain.bin : C# exe returning 1337 directly (no Emit/Expression) -> "false"
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
cat > j0.c <<'C'
#include <sys/mman.h>
#include <string.h>
#include <stdio.h>
static const unsigned char code[] = {0xb8, 0x39, 0x05, 0x00, 0x00, 0xc3};   /* mov eax, 1337 ; ret */
int main(void) {
  void *p = mmap(NULL, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  if (p == MAP_FAILED) return 1;
  memcpy(p, code, sizeof code);
  printf("%d\n", ((int (*)(void))p)());
  return 0;
}
C
cat > j2.c <<'C'
#include <sys/mman.h>
#include <string.h>
#include <stdio.h>
unsigned char jit_buf[] = {0x55, 0x48, 0x89, 0xe5, 0xb8, 0xef, 0xbe, 0xad, 0x0b, 0x5d, 0xc3};
int main(int argc, char **argv) {
  unsigned char *p = mmap(0, 0x1000, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  if (p == MAP_FAILED) return 1;
  memcpy(p, jit_buf, sizeof jit_buf);
  mprotect(p, 0x1000, PROT_READ | PROT_EXEC);
  printf("%x\n", ((unsigned (*)(void))p)());
  return argc > 5;
}
C
cat > d.c <<'C'
#include <sys/mman.h>
#include <string.h>
#include <stdio.h>
static const unsigned char blob[] = {0xb8, 0x39, 0x05, 0x00, 0x00, 0xc3};
int main(void) {
  unsigned char *p = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  if (p == MAP_FAILED) return 1;
  memcpy(p, blob, sizeof blob);
  printf("%02x\n", p[1]);
  return 0;
}
C
gcc -O0 -o "$OUT/rcg_elf_rwx_O0.bin" j0.c
gcc -O2 -s -o "$OUT/rcg_elf_mprotect_O2.bin" j2.c
gcc -O2 -o "$OUT/rcg_decoy_elf_rw.bin" d.c
P='<TargetFramework>net10.0</TargetFramework><Deterministic>true</Deterministic><DebugType>none</DebugType><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable><OutputType>Exe</OutputType>'
mk() { mkdir -p "$1"; printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>%s<AssemblyName>%s</AssemblyName></PropertyGroup></Project>\n' "$P" "$1" > "$1/$1.csproj"; cat > "$1/P.cs"; }
mk DynM <<'CS'
using System; using System.Reflection.Emit;
static class Program {
  static int Main() {
    var dm = new DynamicMethod("GetCode", typeof(int), Type.EmptyTypes);
    ILGenerator il = dm.GetILGenerator();
    il.Emit(OpCodes.Ldc_I4, 0x1337);
    il.Emit(OpCodes.Ret);
    var f = (Func<int>)dm.CreateDelegate(typeof(Func<int>));
    Console.WriteLine(f());
    return 0;
  }
}
CS
mk AsmB <<'CS'
using System; using System.Reflection; using System.Reflection.Emit;
static class Program {
  static int Main() {
    var ab = AssemblyBuilder.DefineDynamicAssembly(new AssemblyName("Gen"), AssemblyBuilderAccess.Run);
    var tb = ab.DefineDynamicModule("Gen").DefineType("Gen.K", TypeAttributes.Public);
    var mb = tb.DefineMethod("Key", MethodAttributes.Public | MethodAttributes.Static, typeof(long), Type.EmptyTypes);
    var il = mb.GetILGenerator();
    il.Emit(OpCodes.Ldc_I8, 0x1122334455667788L);
    il.Emit(OpCodes.Ret);
    var t = tb.CreateType();
    Console.WriteLine(t.GetMethod("Key").Invoke(null, null));
    return 0;
  }
}
CS
mk Expr <<'CS'
using System; using System.Linq.Expressions;
static class Program {
  static int Main() {
    Func<int> f = Expression.Lambda<Func<int>>(Expression.Constant(424242)).Compile();
    Console.WriteLine(f());
    return 0;
  }
}
CS
mk Plain <<'CS'
using System;
static class Program {
  static int Code() { return 0x1337; }
  static int Main() { Console.WriteLine(Code()); return 0; }
}
CS
for p in DynM:rcg_cs_dynmethod AsmB:rcg_cs_asmbuilder Expr:rcg_cs_expr Plain:rcg_decoy_cs_plain; do
  (cd "${p%%:*}" && dotnet build -c Release -o out >/dev/null) && cp "${p%%:*}/out/${p%%:*}.dll" "$OUT/${p##*:}.bin"
done
