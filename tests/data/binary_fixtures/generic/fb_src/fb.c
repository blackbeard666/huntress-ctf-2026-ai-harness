unsigned recover_code(void) { return 34847u; }
unsigned seed_big(void) { return 3000000000u; }
int mix(int x) { return x * 7 + 3; }
int main(int argc, char **argv) { (void)argv; return (int)(recover_code() + seed_big()) + mix(argc); }
