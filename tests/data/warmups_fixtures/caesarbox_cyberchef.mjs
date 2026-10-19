// usage: node caesarbox_cyberchef.mjs HEIGHT  (stdin -> stdout) via CyberChef "Caesar Box Cipher" (deletes spaces; its
// own inverse when HEIGHT = ceil(len / original height) on a full box)
const base = process.env.CC + "/src/core/operations/";
const [h] = process.argv.slice(2);
const Op = (await import(base + "CaesarBoxCipher.mjs")).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
process.stdout.write(new Op().run(input, [parseInt(h, 10)]));
