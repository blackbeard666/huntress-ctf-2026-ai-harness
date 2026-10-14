// usage: node braille_cyberchef.mjs enc|dec  (stdin -> stdout) via CyberChef "To Braille" / "From Braille" (Braille ASCII table)
const base = process.env.CC + "/src/core/operations/";
const [mode] = process.argv.slice(2);
const Op = (await import(base + (mode === "enc" ? "ToBraille.mjs" : "FromBraille.mjs"))).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
process.stdout.write(new Op().run(input, []));
