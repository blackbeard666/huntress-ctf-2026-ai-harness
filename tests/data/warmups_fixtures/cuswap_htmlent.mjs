// usage: node cuswap_htmlent.mjs   (stdin -> stdout) via CyberChef "To HTML Entity" (Convert all characters, Hex entities)
const base = process.env.CC + "/src/core/operations/";
const input = (await new Promise(r => { let d = ""; process.stdin.setEncoding("utf8"); process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const Op = (await import(base + "ToHTMLEntity.mjs")).default;
process.stdout.write(new Op().run(input, [true, "Hex entities"]));
