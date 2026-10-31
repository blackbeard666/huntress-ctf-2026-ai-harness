#include <stdio.h>
#include <string.h>
#ifndef TAG
#define TAG "alpha"
#endif
static const char *cmds[] = {"beacon", "sleep", "upload", "download", "shell", "persist", "exit"};
int dispatch(const char *c) {
    for (unsigned i = 0; i < sizeof cmds / sizeof *cmds; i++)
        if (!strcmp(c, cmds[i])) return (int)i * 7 + 3;
    return -1;
}
int main(int argc, char **argv) {
    printf("agent %s ready\n", TAG);
    for (int i = 1; i < argc; i++) printf("%s -> %d\n", argv[i], dispatch(argv[i]));
    return 0;
}
