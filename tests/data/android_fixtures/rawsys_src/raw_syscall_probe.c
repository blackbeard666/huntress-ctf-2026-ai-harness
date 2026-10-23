/* Hardened anti-hook probes issued as raw syscalls (target native-inline-syscall-stubs): no libc at all (-nostdlib),
   every probe is an inline `syscall` (x86_64) / `svc #0` (arm64) so Frida's libc hooks never see it. The decode key is
   folded from what the kernel answers on a clean, untraced, unrooted device: openat+read+close of /proc/self/status
   (TracerPid 0), faccessat(su) == -ENOENT, newfstatat(/sbin/su) < 0, readlinkat(frida-server) < 0,
   ptrace(PTRACE_TRACEME) != -EPERM, getppid() != 1. ENC = token ^ ((K * (i + 1) + 0x3d) & 0xff), K = the clean fold.
   Clean path: NewStringUTF(token). */
typedef void *(*NewStr)(void *, const char *);
#define NS(env, s) ((NewStr)((*(void ***)(env))[167]))(env, s)
#if defined(__x86_64__)
enum { NR_read = 0, NR_close = 3, NR_ptrace = 101, NR_getppid = 110, NR_openat = 257, NR_newfstatat = 262,
       NR_readlinkat = 267, NR_faccessat = 269 };
static long sc(long n, long a, long b, long c, long d) {
    long r;
    register long r10 __asm__("r10") = d;
    __asm__ volatile("syscall" : "=a"(r) : "a"(n), "D"(a), "S"(b), "d"(c), "r"(r10) : "rcx", "r11", "memory");
    return r;
}
#elif defined(__aarch64__)
enum { NR_read = 63, NR_close = 57, NR_ptrace = 117, NR_getppid = 173, NR_openat = 56, NR_newfstatat = 79,
       NR_readlinkat = 78, NR_faccessat = 48 };
static long sc(long n, long a, long b, long c, long d) {
    register long x8 __asm__("x8") = n, x0 __asm__("x0") = a, x1 __asm__("x1") = b, x2 __asm__("x2") = c,
                  x3 __asm__("x3") = d;
    __asm__ volatile("svc #0" : "+r"(x0) : "r"(x8), "r"(x1), "r"(x2), "r"(x3) : "memory");
    return x0;
}
#endif
static const unsigned char enc[] = ENC;
static char out[64];
static char buf[1024], st[256], lnk[256];
static int tracer_pid(void) {
    long fd = sc(NR_openat, -100, (long)"/proc/self/status", 0, 0);
    if (fd < 0) return -1;
    long n = sc(NR_read, fd, (long)buf, sizeof buf - 1, 0);
    sc(NR_close, fd, 0, 0, 0);
    if (n <= 0) return -1;
    buf[n] = 0;
    for (long i = 0; i + 10 < n; i++) {
        const char *t = "TracerPid:";
        int j = 0;
        while (j < 10 && buf[i + j] == t[j]) j++;
        if (j < 10) continue;
        long p = i + 10, v = 0;
        while (buf[p] == ' ' || buf[p] == '\t') p++;
        while (buf[p] >= '0' && buf[p] <= '9') v = v * 10 + (buf[p++] - '0');
        return (int)v;
    }
    return -1;
}
__attribute__((visibility("default"))) void *Java_com_huntress_arena_Guard_nativeCheck(void *env, void *thiz) {
    unsigned k = 0x5a;
    int tp = tracer_pid();
    k += tp == 0 ? 0x13 : tp < 0 ? 0x99 : 0x41;
    k ^= sc(NR_faccessat, -100, (long)"/system/xbin/su", 0, 0) == -2 ? 0x0c : 0x66;
    k += sc(NR_newfstatat, -100, (long)"/sbin/su", (long)st, 0) < 0 ? 7 : 0x50;
    k ^= sc(NR_readlinkat, -100, (long)"/data/local/tmp/frida-server", (long)lnk, sizeof lnk) < 0 ? 0x21 : 0x77;
    k += sc(NR_ptrace, 0, 0, 0, 0) != -1 ? 3 : 0x31;
    k ^= sc(NR_getppid, 0, 0, 0, 0) != 1 ? 0x40 : 0x08;
    k &= 0xff;
    unsigned i = 0;
    for (; i < sizeof enc && i < 63; i++) out[i] = (char)(enc[i] ^ ((k * (i + 1) + 0x3d) & 0xff));
    out[i] = 0;
    return NS(env, out);
}
