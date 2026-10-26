// Independent Deadfish reader (esolangs.org/wiki/Deadfish semantics), never lib/: reads $encoded, runs it, prints the
// output bytes as UTF-8. argv[2] = "idso" (classic) or "xkcd" (x inc, d dec, k square, c output). Exits 1 on a char
// outside the dialect, no output, or a control byte (the line is not a text-printing Deadfish program).
const dialect = process.argv[2] || "idso";
const ops = dialect === "xkcd" ? { x: "inc", d: "dec", k: "sqr", c: "out" } : { i: "inc", d: "dec", s: "sqr", o: "out" };
const src = (process.env.encoded || "").toLowerCase();
let acc = 0;
const bytes = [];
for (const ch of src) {
  if (/\s/.test(ch)) continue;
  const op = ops[ch];
  if (!op) { console.error(`foreign char ${JSON.stringify(ch)}`); process.exit(1); }
  if (op === "inc") acc = acc + 1;
  else if (op === "dec") acc = acc - 1;
  else if (op === "sqr") acc = acc * acc;
  else bytes.push(acc);
  if (acc === 256 || acc === -1) acc = 0;
}
if (!bytes.length || bytes.some((b) => b < 9 || (b > 13 && b < 32) || b === 127 || b > 255)) {
  console.error(`no text output: ${JSON.stringify(bytes.slice(0, 8))}`);
  process.exit(1);
}
process.stdout.write(new TextDecoder("utf-8", { fatal: true }).decode(Uint8Array.from(bytes)));
