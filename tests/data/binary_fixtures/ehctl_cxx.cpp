#include <cstdio>
#include <stdexcept>
static volatile int g;
__attribute__((noinline)) int check_key(int k) {
    if (k != 1337) throw std::runtime_error("bad");
    return 42;
}
__attribute__((noinline)) int real_path(int k) {
    try { return check_key(k); }
    catch (const std::runtime_error &e) { g = 7; return 0x4843; }
}
int main(int c, char **v) { std::printf("%d\n", real_path(c)); return 0; }
