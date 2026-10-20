// usage: node altbase_cyberchef.mjs b32|b64 <alphabet incl. pad char> [nopad]  (stdin -> stdout) via CyberChef "To Base32" / "To Base64"
const base = process.env.CC + "/src/core/operations/";
const [mode, alpha, nopad] = process.argv.slice(2);
const Op = (await import(base + (mode === "b32" ? "ToBase32.mjs" : "ToBase64.mjs"))).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
let out = new Op().run(new TextEncoder().encode(input).buffer, [alpha]);
const n = mode === "b32" ? 32 : 64, chars = Array.from(alpha), padc = chars[chars.length - 1];
if (nopad) out = out.replace(new RegExp("[" + padc.replace(/[\]\\^-]/g, "\\$&") + "]+$"), "");
process.stdout.write(out);
