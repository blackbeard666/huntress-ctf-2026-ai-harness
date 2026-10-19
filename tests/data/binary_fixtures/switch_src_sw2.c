#include <stdio.h>
#include <stdlib.h>
__attribute__((noinline)) int op_add(int a){puts("add");return a+1;}
__attribute__((noinline)) int op_sub(int a){puts("sub");return a+8;}
__attribute__((noinline)) int op_mul(int a){puts("mul");return a+15;}
__attribute__((noinline)) int op_div(int a){puts("div");return a+22;}
__attribute__((noinline)) int op_xor(int a){puts("xor");return a+29;}
__attribute__((noinline)) int op_shl(int a){puts("shl");return a+36;}
__attribute__((noinline)) int op_neg(int a){puts("neg");return a+43;}
__attribute__((noinline)) int op_rol(int a){puts("rol");return a+50;}
__attribute__((noinline)) int op_inc(int a){puts("inc");return a+57;}
__attribute__((noinline)) int op_dec(int a){puts("dec");return a+64;}
__attribute__((noinline)) int op_not(int a){puts("not");return a+71;}
__attribute__((noinline)) int op_sqr(int a){puts("sqr");return a+78;}
__attribute__((noinline)) int op_bad(int a){puts("bad");return 0;}
__attribute__((noinline)) int dispatch(int op,int a){int r;switch(op){
 case 2: r=op_add(a); break;
 case 3: r=op_sub(a); break;
 case 4: r=op_mul(a); break;
 case 5: r=op_div(a); break;
 case 6: r=op_xor(a); break;
 case 7: r=op_shl(a); break;
 case 8: r=op_neg(a); break;
 case 9: r=op_rol(a); break;
 case 10: r=op_inc(a); break;
 case 11: r=op_dec(a); break;
 case 12: r=op_not(a); break;
 case 13: r=op_sqr(a); break;
 default: r=op_bad(a);}
 return r*5+1;}
int main(int c,char**v){return dispatch(atoi(v[1]),c);}
