#include <stdio.h>
#include <stdlib.h>
__attribute__((noinline)) int op_add(int a){puts("add");return a+1;}
__attribute__((noinline)) int op_sub(int a){puts("sub");return a-1;}
__attribute__((noinline)) int op_mul(int a){puts("mul");return a*3;}
__attribute__((noinline)) int op_div(int a){puts("div");return a/2;}
__attribute__((noinline)) int op_xor(int a){puts("xor");return a^7;}
__attribute__((noinline)) int op_shl(int a){puts("shl");return a<<2;}
__attribute__((noinline)) int op_neg(int a){puts("neg");return -a;}
__attribute__((noinline)) int op_bad(int a){puts("bad");return 0;}
__attribute__((noinline)) int dispatch(int op, int a){
  int r;
  switch(op){
  case 3: r=op_add(a); break;
  case 4: r=op_sub(a); break;
  case 5: r=op_mul(a); break;
  case 6: r=op_div(a); break;
  case 8: r=op_xor(a); break;
  case 9: r=op_shl(a); break;
  case 10: r=op_neg(a); break;
  default: r=op_bad(a); break;
  }
  return r*5+1;
}
int main(int c,char**v){return dispatch(atoi(v[1]),c);}
