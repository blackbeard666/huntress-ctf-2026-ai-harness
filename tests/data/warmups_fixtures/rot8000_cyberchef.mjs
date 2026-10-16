// usage: node rot8000_cyberchef.mjs  (stdin -> stdout) via CyberChef "ROT8000" (an involution: same op encodes and decodes)
const base = process.env.CC + "/src/core/operations/";
const Op = (await import(base + "ROT8000.mjs")).default;
const input = (await new Promise(r => { let d = ""; process.stdin.setEncoding("utf8"); process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
process.stdout.write(new Op().run(input, []));
