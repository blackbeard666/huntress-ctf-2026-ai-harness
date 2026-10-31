/* gf-macho fixture source: custom __TEXT,__hctf and __DATA,__cfg sections + a few globals */
__attribute__((section("__TEXT,__hctf"), used)) const char hctf_tag[] = "HCTF-MO-TAG";
__attribute__((section("__DATA,__cfg"), used)) char cfg_blob[32] = "cfg=1;mode=macho";
int counter = 3;
static int helper(int x) { return x * counter + 1; }
int exported_fn(int a) { return helper(a) ^ 0x5a; }
int main(int argc, char **argv) { (void)argv; return exported_fn(argc) & 1; }
