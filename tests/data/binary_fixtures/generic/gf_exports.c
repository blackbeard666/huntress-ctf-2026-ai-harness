int ie_alpha(int x) { return x + 1; }
int ie_beta(int x) { return x * 2; }
int ie_gamma = 7;
static int ie_hidden(int x) { return x; }
int ie_use(int x) { return ie_hidden(x); }
