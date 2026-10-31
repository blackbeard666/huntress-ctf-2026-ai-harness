#include <windows.h>
#include <stdio.h>
#include <winsock2.h>
__declspec(dllexport) int ie_pe_alpha(int x) { return x + 1; }
__declspec(dllexport) int ie_pe_beta(int x) { return x * 2; }
int main(void) { WSADATA w; WSAStartup(0x202, &w); printf("%lu\n", GetTickCount()); MessageBoxA(0, "x", "y", 0); return 0; }
