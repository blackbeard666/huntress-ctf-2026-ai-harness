// usage: node cc.mjs enc|dec  (stdin -> stdout) via CyberChef "Convert Leet Speak"
const base = process.env.CC + "/src/core/operations/";
const Op = (await import(base + "ConvertLeetSpeak.mjs")).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
process.stdout.write(new Op().run(input, [process.argv[2] === "enc" ? "To Leet Speak" : "From Leet Speak"]));
