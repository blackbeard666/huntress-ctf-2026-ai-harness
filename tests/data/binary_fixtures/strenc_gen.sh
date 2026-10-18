#!/bin/bash
# strenc_gen.sh <out.bin> <xor|add|none> "<gcc flags>" <key:string>...   (prefix a spec with "stack:" for a stack array)
# perl encrypts each string with its own 1-byte key (xor: c=p^k, decoder p=c^k; add: c=p+k, decoder p=c-k; none:
# decoy -- a shared noinline checksum(ptr,len,seed) over random tables, nothing printable; plain: decoy -- cleartext
# strings through a shared noinline emit(ptr,len,fd-ish key)) and gcc compiles a C
# program whose shared noinline decoder dstr(ptr,len,key) is called once per string, in spec order; .rodata arrays
# for plain specs, local (stack-built) arrays for stack: specs. The program prints the decoded strings, one per line.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
out=$1 alg=$2 flags=$3; shift 3
mkdir -p "$here/strenc_src"
src="$here/strenc_src/$(basename "$out" .bin).c"
perl - "$alg" "$@" > "$src" <<'PL'
my ($alg, @specs) = @ARGV;
my $op = $alg eq 'xor' ? 's[i] ^ k' : $alg eq 'add' ? '(unsigned char)(s[i] - k)' : '0';
print "#include <stdio.h>\n#include <stdlib.h>\n";
if ($alg eq 'plain') {
  print "__attribute__((noinline)) char *dstr(const unsigned char *s, unsigned n, unsigned char k) { fwrite(s, 1, n, k == 2 ? stderr : stdout); return (char *)s; }\n";
} elsif ($alg eq 'none') {
  print "__attribute__((noinline)) unsigned dstr(const unsigned char *s, unsigned n, unsigned char k) { unsigned h = k; for (unsigned i = 0; i < n; i++) h = h * 31 + s[i]; return h; }\n";
} else {
  print "__attribute__((noinline)) char *dstr(const unsigned char *s, unsigned n, unsigned char k) { char *o = malloc(n + 1); for (unsigned i = 0; i < n; i++) o[i] = $op; o[n] = 0; return o; }\n";
}
my ($i, @body, @glob) = (0);
srand(7);
for my $sp (@specs) {
  my $stack = $sp =~ s/^stack://;
  my ($k, $str) = split /:/, $sp, 2;
  $k = hex $k;
  my @b = $alg eq 'none' ? map { int rand 256 } 1 .. length $str : $alg eq 'plain' ? map { ord } split //, $str
        : map { $alg eq 'xor' ? (ord($_) ^ $k) : ((ord($_) + $k) & 255) } split //, $str;
  my $arr = join ',', map { sprintf '0x%02x', $_ } @b;
  my $n = scalar @b;
  if ($stack) { push @body, "  { unsigned char e$i\[] = {$arr}; r[$i] = dstr(e$i, $n, $k); }" }
  else { push @glob, "static const unsigned char e$i\[] = {$arr};"; push @body, "  r[$i] = dstr(e$i, $n, $k);" }
  $i++;
}
print "$_\n" for @glob;
my $ty = $alg eq 'none' ? 'unsigned' : 'char *';
print "int main(void) {\n  $ty r[$i];\n", join("\n", @body), "\n";
print $alg eq 'plain' ? "  (void)r;\n" : $alg eq 'none' ? "  for (int j = 0; j < $i; j++) printf(\"%08x\\n\", r[j]);\n" : "  for (int j = 0; j < $i; j++) puts(r[j]);\n";
print "  return 0;\n}\n";
PL
gcc $flags -o "$out" "$src"
