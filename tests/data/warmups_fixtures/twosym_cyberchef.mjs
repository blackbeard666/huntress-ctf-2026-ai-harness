// usage: node twosym_cyberchef.mjs <sym0> <sym1> <width> <hex|ascii>  (stdin -> stdout)
// symbols -> 0/1 (code-point aware, whitespace dropped, U+FE0F ignored), CyberChef 'From Binary' (Byte Length=width);
// hex: each group value is one hex digit -> CyberChef 'From Hex'; result decoded as UTF-8.
const base = process.env.CC + "/src/core/operations/";
const [s0, s1, width, inner] = process.argv.slice(2);
const FromBinary = (await import(base + "FromBinary.mjs")).default;
const FromHex = (await import(base + "FromHex.mjs")).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const bits = Array.from(input.replace(/️/g, "")).filter(c => !/\s/.test(c))
    .map(c => c === s0 ? "0" : c === s1 ? "1" : "?").join("");
let bytes = new FromBinary().run(bits, ["None", Number(width)]);
if (inner === "hex") bytes = new FromHex().run(bytes.map(v => v.toString(16)).join(""), ["None"]);
process.stdout.write(new TextDecoder("utf-8", { fatal: true }).decode(Uint8Array.from(bytes)));
