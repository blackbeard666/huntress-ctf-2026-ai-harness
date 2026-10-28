#include <stdio.h>
int event_success(int x) { return x + 1; }
int event_failure(int x) { return x - 1; }
int event_decoy(int x) { return x * 3; }
static const char tag[] = "decoy-branch-marker";
int main(int argc, char **argv) { if (argc > 3) puts(tag); return event_success(argc) + event_failure(argc) + event_decoy(argc); }
