// usage: node morse_cyberchef.mjs enc <format> <letterDelim> <wordDelim> | dec <letterDelim> <wordDelim>  (stdin -> stdout)
// via CyberChef "To Morse Code" / "From Morse Code" (npm cyberchef); format e.g. '-/.', '_/.', 'Dash/Dot'
const base = process.env.CC + "/src/core/operations/";
const [mode, ...args] = process.argv.slice(2);
const Op = (await import(base + (mode === "enc" ? "ToMorseCode.mjs" : "FromMorseCode.mjs"))).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
process.stdout.write(new Op().run(input, args));
