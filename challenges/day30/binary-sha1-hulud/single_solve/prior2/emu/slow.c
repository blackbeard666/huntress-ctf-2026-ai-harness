#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
int main(int c,char**v){uint64_t rcx=strtoull(v[1],0,16),rsi=strtoull(v[2],0,16);uint64_t N=strtoull(v[3],0,16);
FILE*f=fopen(v[4],"rb");unsigned char*b=malloc(rsi+16);fread(b,1,rsi,f);uint64_t r8=rsi-7,rbx=0xf8714df9dba9a23dULL,last=0;
for(uint64_t i=0;i<N;i++){uint64_t r10=((rcx>>32)*r8)>>32;uint64_t x=0;unsigned char t[8];
 if(r10+8>rsi){for(int k=0;k<8;k++)t[k]=b[(r10+k)%rsi];}else memcpy(t,b+r10,8);
 memcpy(&x,t,8);last=x;rcx^=x;rcx*=rbx;rcx^=rcx>>29;}
printf("%llx %llx\n",(unsigned long long)rcx,(unsigned long long)last);}
