// usage: node byterot_cyberchef.mjs <left|right> <amount> <in: text|hex|base64> <out: text|hex|base64>  (stdin -> stdout)
// via CyberChef "Rotate left" / "Rotate right" (per-byte, Carry through off)
const base = process.env.CC + "/src/core/operations/";
const [dir, amt, inf, outf] = process.argv.slice(2);
const Op = (await import(base + (dir === "left" ? "RotateLeft.mjs" : "RotateRight.mjs"))).default;
const raw = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const input = inf === "text" ? Buffer.from(raw, "utf8") : Buffer.from(raw.replace(/\s+/g, ""), inf);
const out = Buffer.from(new Op().run(Array.from(input), [parseInt(amt, 10), false]));
process.stdout.write(outf === "text" ? out.toString("utf8") : out.toString(outf));
