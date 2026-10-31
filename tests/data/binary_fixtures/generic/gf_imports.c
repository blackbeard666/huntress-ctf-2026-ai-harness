#include <stdio.h>
#include <math.h>
#include <zlib.h>
int main(int argc, char **argv) { printf("%f %s\n", sqrt((double)argc), zlibVersion()); return 0; }
