#define _GNU_SOURCE
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static volatile int stage;
void trap_handler(int s) { stage = 0x48434647; }
void ill_handler(int s, siginfo_t *i, void *u) { ((ucontext_t*)u)->uc_mcontext.gregs[REG_RIP] += 2; stage++; }
void segv_handler(int s) { exit(3); }
int main(void) {
    struct sigaction sa; memset(&sa, 0, sizeof sa);
    sa.sa_handler = trap_handler;
    sigaction(SIGTRAP, &sa, NULL);
    struct sigaction sb; memset(&sb, 0, sizeof sb);
    sb.sa_sigaction = ill_handler; sb.sa_flags = SA_SIGINFO;
    sigaction(SIGILL, &sb, NULL);
    signal(SIGSEGV, segv_handler);
    __asm__ volatile("int3");
    __asm__ volatile("ud2");
    printf("%x\n", stage);
    return stage == 0x48434648 ? 0 : 1;
}
