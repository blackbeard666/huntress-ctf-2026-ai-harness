// usage: node base62_cyberchef.mjs enc|dec <alphabet>  (stdin -> stdout) via CyberChef "To Base62" / "From Base62"
const base = process.env.CC + "/src/core/operations/";
const [mode, alpha] = process.argv.slice(2);
const Op = (await import(base + (mode === "enc" ? "ToBase62.mjs" : "FromBase62.mjs"))).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const out = new Op().run(mode === "enc" ? new TextEncoder().encode(input).buffer : input, [alpha]);
process.stdout.write(mode === "enc" ? out : Buffer.from(out).toString("utf8"));
