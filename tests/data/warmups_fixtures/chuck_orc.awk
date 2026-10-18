# Chuck Norris unary decoder (independent gawk impl). usage: gawk -v W=7 [-v HEX=1] -f orc.awk
{ n = split($0, t, " "); bits = ""; for (i = 1; i < n; i += 2) { c = (t[i] == "0") ? "1" : "0"; for (j = 0; j < length(t[i+1]); j++) bits = bits c }
  out = ""; for (i = 1; i <= length(bits); i += W) { v = 0; for (j = 0; j < W; j++) v = v * 2 + substr(bits, i + j, 1); out = out sprintf("%c", v) }
  if (HEX) { h = out; out = ""; for (i = 1; i <= length(h); i += 2) out = out sprintf("%c", strtonum("0x" substr(h, i, 2))) }
  printf "%s", out }
