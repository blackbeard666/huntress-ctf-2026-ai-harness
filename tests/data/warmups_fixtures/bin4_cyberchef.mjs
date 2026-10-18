// usage: node bin4_cyberchef.mjs <FromBinary delimiter: Space|Comma|None|...> [rol4]  (stdin -> stdout)
// CyberChef 'From Binary' (Byte Length=4) -> each 4-bit value is one hex digit -> 'From Hex' -> [optional 'Rotate left'
// 4 bits = nibble swap] -> UTF-8 (fatal: a non-UTF-8 result throws).
const base = process.env.CC + "/src/core/operations/";
const [delim, rol] = process.argv.slice(2);
const FromBinary = (await import(base + "FromBinary.mjs")).default;
const FromHex = (await import(base + "FromHex.mjs")).default;
const RotateLeft = (await import(base + "RotateLeft.mjs")).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const vals = new FromBinary().run(input, [delim, 4]);
let bytes = new FromHex().run(vals.map(v => v.toString(16)).join(""), ["None"]);
if (rol === "rol4") bytes = new RotateLeft().run(bytes, [4, false]);
process.stdout.write(new TextDecoder("utf-8", { fatal: true }).decode(Uint8Array.from(bytes)));
