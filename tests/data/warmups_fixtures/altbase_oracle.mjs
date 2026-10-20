// usage: node altbase_oracle.mjs <64-or-32 data chars> [pad char]  (stdin -> stdout): npm rfc4648 codec.parse over a custom
// alphabet (bits = log2 len), or `crockford` -> npm base32-decode 'Crockford'. Errors -> exit 1 (not this encoding).
const M = process.env.AB + "/node_modules/";
const [chars, pad] = process.argv.slice(2);
let s = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).trim();
let bytes;
if (chars === "crockford") {
  bytes = new Uint8Array((await import(M + "base32-decode/index.js")).default(s.replace(/-/g, "").replace(/=+$/, ""), "Crockford"));
} else {
  const { codec } = await import(M + "rfc4648/lib/rfc4648.js");
  if (pad) while (s.endsWith(pad)) s = s.slice(0, -1);
  bytes = codec.parse(s, { chars, bits: chars.length === 64 ? 6 : 5 }, { loose: true });
}
process.stdout.write(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
