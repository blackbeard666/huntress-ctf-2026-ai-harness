int pg_lib_one(int x) { return x ^ 0x5a; }
int pg_lib_two(int x) { return x << 2; }
int pg_lib_three(int x) { return pg_lib_one(x) + pg_lib_two(x); }
