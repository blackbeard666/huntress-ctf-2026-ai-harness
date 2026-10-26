// Independent oracle for the full-Brainfuck fixtures (never lib/): a plain char-at-a-time JS interpreter.
// Usage: encoded=... node bff_oracle.mjs [bits=8|16] [eof=0|-1] [peel=b64gz]
// Non-command chars are comments; ',' stores `eof`; output = cell values as UTF-8 bytes (8-bit) or code points.
import { gunzipSync } from "node:zlib";
const args = Object.fromEntries(process.argv.slice(2).map((a) => a.split("=")));
const bits = Number(args.bits ?? 8), eof = Number(args.eof ?? 0), M = 2 ** bits;
let t = process.env.encoded;
if (args.peel === "b64gz") t = gunzipSync(Buffer.from(t.replace(/\s/g, ""), "base64")).toString("utf8");
const code = [...t].filter((c) => "+-<>[].,".includes(c));
const jmp = {}, st = [];
code.forEach((c, i) => { if (c === "[") st.push(i); else if (c === "]") { const k = st.pop(); jmp[k] = i; jmp[i] = k; } });
const tape = new Array(65536).fill(0), out = [];
for (let i = 0, p = 0; i < code.length; i++) {
  const c = code[i];
  if (c === "+") tape[p] = (tape[p] + 1) % M;
  else if (c === "-") tape[p] = (tape[p] - 1 + M) % M;
  else if (c === ">") p = (p + 1) % 65536;
  else if (c === "<") p = (p + 65535) % 65536;
  else if (c === ".") out.push(tape[p]);
  else if (c === ",") tape[p] = ((eof % M) + M) % M;
  else if (c === "[" && !tape[p]) i = jmp[i];
  else if (c === "]" && tape[p]) i = jmp[i];
}
process.stdout.write(bits === 8 ? new TextDecoder("utf-8", { fatal: true }).decode(new Uint8Array(out))
  : String.fromCodePoint(...out));
