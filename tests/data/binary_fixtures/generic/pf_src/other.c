#include <stdio.h>
#include <stdlib.h>
#include "blob.h"
static const char tag[] = "pf stranger sample: bubble sorter";
static void sort(int *a, int n) { for (int i = 0; i < n; i++) for (int j = 0; j + 1 < n - i; j++) if (a[j] > a[j+1]) { int t = a[j]; a[j] = a[j+1]; a[j+1] = t; } }
int main(int argc, char **argv) { int a[8]; for (int i = 0; i < 8; i++) a[i] = atoi(argc > 1 ? argv[1] : "3") * (7 - i); sort(a, 8); printf("%s %d %d %d\n", tag, a[0], a[7], hcfg_blob[4]); return 0; }
