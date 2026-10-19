#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef int (*op_t)(int);
__attribute__((noinline)) int op_add(int x){ return x + 7; }
__attribute__((noinline)) int op_mul(int x){ return x * 3; }
__attribute__((noinline)) int op_neg(int x){ return -x; }
__attribute__((noinline)) int op_log(int x){ printf("log %d\n", x); return x; }
op_t table[3] = { op_add, op_mul, op_neg };
static volatile op_t gptr = op_log;
__attribute__((noinline)) int dispatch(int i, int x){ return table[i % 3](x); }
__attribute__((noinline)) int via_reg(int x){ op_t f = op_mul; __asm__("" : "+r"(f)); return f(x) + puts("reg"); }
__attribute__((noinline)) int via_global(int x){ return gptr(x); }
__attribute__((noinline)) void unused_helper(void){ puts("never"); }
int main(int argc, char **argv){
  int x = argc > 1 ? atoi(argv[1]) : 2;
  x = dispatch(x, x);
  x += via_reg(x);
  x += via_global(x);
  if (strlen(argv[0]) > 1000) exit(3);
  printf("%d\n", x);
  return 0;
}
