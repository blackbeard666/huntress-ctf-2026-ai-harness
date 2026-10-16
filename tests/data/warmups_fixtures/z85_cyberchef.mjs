// usage: node z85_cyberchef.mjs enc|dec  (stdin -> stdout) via CyberChef "To Base85" / "From Base85" with the
// "Z85 (ZeroMQ)" alphabet option (partial final group truncated, ascii85-style)
const base = process.env.CC + "/src/core/operations/";
const mode = process.argv[2];
const Z85 = "0-9a-zA-Z.\\-:+=^!/*?&<>()[]{}@%$#";
const Op = (await import(base + (mode === "enc" ? "ToBase85.mjs" : "FromBase85.mjs"))).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const op = new Op();
const out = mode === "enc" ? op.run(new TextEncoder().encode(input).buffer, [Z85, false]) : op.run(input, [Z85, false, ""]);
process.stdout.write(mode === "enc" ? out : Buffer.from(out).toString("utf8"));
