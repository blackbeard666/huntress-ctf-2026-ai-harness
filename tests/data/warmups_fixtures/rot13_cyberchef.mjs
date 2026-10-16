// usage: node rot13_cyberchef.mjs <amount> <lower 0|1> <upper 0|1> <numbers 0|1>  (stdin -> stdout) via CyberChef "ROT13"
const base = process.env.CC + "/src/core/operations/";
const Op = (await import(base + "ROT13.mjs")).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const [amt, lo, up, num] = process.argv.slice(2);
const out = new Op().run(new TextEncoder().encode(input), [lo === "1", up === "1", num === "1", parseInt(amt, 10)]);
process.stdout.write(new TextDecoder().decode(new Uint8Array(out)));
