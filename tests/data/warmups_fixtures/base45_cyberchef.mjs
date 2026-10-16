// usage: node base45_cyberchef.mjs enc|dec  (stdin -> stdout) via CyberChef "To Base45" / "From Base45" (RFC 9285 alphabet)
const base = process.env.CC + "/src/core/operations/";
const mode = process.argv[2];
const Op = (await import(base + (mode === "enc" ? "ToBase45.mjs" : "FromBase45.mjs"))).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const op = new Op();
const out = op.run(mode === "enc" ? new TextEncoder().encode(input).buffer : input, op.args.map(a => a.value));
process.stdout.write(mode === "enc" ? out : Buffer.from(out).toString("utf8"));
