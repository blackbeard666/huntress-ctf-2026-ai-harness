// Independent oracle for the Brainfuck token-dialect fixtures (never lib/): map the dialect's tokens back to
// Brainfuck by the esolangs.org tables, run it in a plain JS interpreter, print the output.
// Usage: encoded=... node bfd_oracle.mjs <ook|cow|pikalang|alphuck|reversefuck|binaryfuck|map> [map-json]
const [dialect, mapJson] = process.argv.slice(2);
const t = process.env.encoded.trim();
const OPS = "><+-.,[]";
const zip = (ks) => Object.fromEntries(ks.map((k, i) => [k, OPS[i]]));
let toks, m;
if (dialect === "ook") {
  const marks = [...t.matchAll(/(?:Ook|Blub)?\s*([.?!])/gi)].map((x) => x[1]);
  m = zip([".?", "?.", "..", "!!", "!.", ".!", "!?", "?!"]);
  toks = [];
  for (let i = 0; i < marks.length; i += 2) toks.push(marks[i] + marks[i + 1]);
} else if (dialect === "cow") {
  m = { ...zip("moO mOo MoO MOo Moo oom MOO moo".split(" ")), OOO: "[-]" };
  toks = t.split(/\s+/);
} else if (dialect === "pikalang") {
  m = zip("pipi pichu pi ka pikachu pikapi pika chu".split(" "));
  toks = t.split(/\s+/);
} else if (dialect === "binaryfuck") {
  m = zip("000 001 010 011 100 101 110 111".split(" "));
  toks = t.replace(/\s/g, "").match(/.{3}/g);
} else if (dialect === "alphuck" || dialect === "reversefuck") {
  m = zip([...(dialect === "alphuck" ? "aceijops" : "<>-+.,[]")]);
  toks = [...t.replace(/\s/g, "")];
} else {
  m = JSON.parse(mapJson);
  toks = t.split(/\s+/);
}
const code = toks.map((x) => { if (!(x in m)) throw new Error("token " + x); return m[x]; }).join("");
const tape = new Uint8Array(65536), out = [], st = [], jmp = {};
for (let i = 0; i < code.length; i++) {
  if (code[i] === "[") st.push(i);
  else if (code[i] === "]") { const k = st.pop(); jmp[k] = i; jmp[i] = k; }
}
for (let i = 0, p = 0; i < code.length; i++) {
  const c = code[i];
  if (c === "+") tape[p]++;
  else if (c === "-") tape[p]--;
  else if (c === ">") p++;
  else if (c === "<") p--;
  else if (c === ".") out.push(tape[p]);
  else if (c === "[" && !tape[p]) i = jmp[i];
  else if (c === "]" && tape[p]) i = jmp[i];
}
process.stdout.write(new TextDecoder("utf-8", { fatal: true }).decode(new Uint8Array(out)));
