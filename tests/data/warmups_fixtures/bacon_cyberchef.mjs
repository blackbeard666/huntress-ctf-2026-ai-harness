// usage: node cc.mjs enc|dec <alphabet> <translation> <keep:0|1> <invert:0|1>  (stdin -> stdout) via CyberChef ops
const base = process.env.CC + "/src/core/operations/";
const [mode, alpha, tr, keep, inv] = process.argv.slice(2);
const Op = (await import(base + (mode === "enc" ? "BaconCipherEncode.mjs" : "BaconCipherDecode.mjs"))).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const args = mode === "enc" ? [alpha, tr, keep === "1", inv === "1"] : [alpha, tr, inv === "1"];
process.stdout.write(new Op().run(input, args));
