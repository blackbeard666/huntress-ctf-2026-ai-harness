// Independent oracle for the generic stack / register toy-VM fixtures (node, its own interpreter, not lib/).
// stack: PUSH n | ADD | SUB | OUT (pops) | HALT ; reg: MOV r, n | ADD r, n | SUB r, n | PRINT r | HALT.
// Usage: node vmlisting_oracle.mjs < program  -> prints the output; exits 1 on an unknown instruction / no output.
import { readFileSync } from "node:fs";
const src = readFileSync(0, "utf8");
const num = (t) => /^-?\d+$/.test(t) ? parseInt(t, 10) : /^0x[0-9a-f]+$/i.test(t) ? parseInt(t, 16) : null;
const st = [], reg = {}, out = [];
for (const raw of src.split(/\r?\n/)) {
  const line = raw.split(";")[0].trim();
  if (!line) continue;
  const [op, ...rest] = line.split(/[\s,]+/).filter(Boolean);
  const u = op.toUpperCase();
  const v = (t) => num(t) ?? (reg[t] ?? 0);
  if (u === "PUSH") st.push(v(rest[0]));
  else if (u === "OUT") out.push(st.pop());
  else if (u === "MOV") reg[rest[0]] = v(rest[1]);
  else if ((u === "ADD" || u === "SUB") && rest.length === 2) reg[rest[0]] += (u === "ADD" ? 1 : -1) * v(rest[1]);
  else if (u === "ADD" || u === "SUB") { const b = st.pop(), a = st.pop(); st.push(u === "ADD" ? a + b : a - b); }
  else if (u === "PRINT") out.push(v(rest[0]));
  else if (u === "HALT") break;
  else { process.stderr.write(`unknown ${op}\n`); process.exit(1); }
}
if (!out.length) process.exit(1);
process.stdout.write(Buffer.from(out).toString("utf8"));
