// usage: node rail_cyberchef.mjs enc|dec KEY OFFSET  (stdin -> stdout) via CyberChef "Rail Fence Cipher Encode" / "Decode"
const base = process.env.CC + "/src/core/operations/";
const [mode, key, offset] = process.argv.slice(2);
const Op = (await import(base + (mode === "enc" ? "RailFenceCipherEncode.mjs" : "RailFenceCipherDecode.mjs"))).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
process.stdout.write(new Op().run(input, [parseInt(key, 10), parseInt(offset, 10)]));
