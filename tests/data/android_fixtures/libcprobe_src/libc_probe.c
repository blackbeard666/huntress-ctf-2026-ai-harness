/* Native anti-debug probes inside the JNI export (target native-libc-probe-stubs-emulate, row 66): the decode key is
   folded from what libc answers on a clean, untraced device -- /proc/self/status TracerPid (read char by char after
   strncmp), /proc/self/maps lines strstr'd for frida/xposed, access(su) == -1, a pthread watchdog run once (joined),
   ptrace(PTRACE_TRACEME) == 0, prctl(PR_SET_DUMPABLE) == 0, a fork() watchdog child that only the child runs, and a
   clock_gettime() delta. ENC = token ^ ((K * (i + 1) + 0x3d) & 0xff) with K = KEY (the clean fold) -- no literal key
   in the .so, and any probe answered "debugged" yields garbage. Clean path: NewStringUTF(token). */
#include <fcntl.h>
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/ptrace.h>
#include <time.h>
#include <unistd.h>
typedef void *(*NewStr)(void *, const char *);
#define NS(env, s) ((NewStr)((*(void ***)(env))[167]))(env, s)
static const unsigned char enc[] = ENC;
static char out[64];
static volatile int g_ok;
static int tracer_pid(void) {
    FILE *f = fopen("/proc/self/status", "r");
    char line[256];
    int tp = -1;
    if (!f) return -1;
    while (fgets(line, sizeof line, f))
        if (strncmp(line, "TracerPid:", 10) == 0) { tp = atoi(line + 10); break; }
    fclose(f);
    return tp;
}
static void *watchdog(void *arg) { *(volatile int *)arg = tracer_pid() == 0 ? 0x21 : 0x77; return 0; }
__attribute__((visibility("default"))) void *Java_com_huntress_arena_Guard_nativeCheck(void *env, void *thiz) {
    struct timespec t0, t1;
    unsigned k = 0x5a;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    int tp = tracer_pid();
    k += tp == 0 ? 0x13 : 0x41;
    int fd = open("/proc/self/maps", O_RDONLY);
    if (fd >= 0) {
        char buf[4096];
        long n = read(fd, buf, sizeof buf - 1);
        close(fd);
        buf[n > 0 ? n : 0] = 0;
        k ^= (strstr(buf, "frida") || strstr(buf, "xposed")) ? 0x66 : 0x0c;
    } else k ^= 0x99;
    k += access("/system/xbin/su", F_OK) == -1 ? 7 : 0x50;
    pthread_t th;
    if (pthread_create(&th, 0, watchdog, (void *)&g_ok) == 0) pthread_join(th, 0);
    k ^= g_ok;
    k += ptrace(PTRACE_TRACEME, 0, 0, 0) == 0 ? 3 : 0x31;
    k ^= prctl(PR_SET_DUMPABLE, 0, 0, 0, 0) == 0 ? 0x40 : 0x08;
    pid_t p = fork();
    if (p == 0) { if (getppid() == 1) kill(getpid(), SIGKILL); _exit(0); }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    if (t1.tv_sec - t0.tv_sec > 2) k ^= 0xff;
    k &= 0xff;
    unsigned i = 0;
    for (; i < sizeof enc && i < 63; i++) out[i] = (char)(enc[i] ^ ((k * (i + 1) + 0x3d) & 0xff));
    out[i] = 0;
    return NS(env, out);
}
