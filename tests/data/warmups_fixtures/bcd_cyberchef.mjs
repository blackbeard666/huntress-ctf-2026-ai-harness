// usage: node bcd_cyberchef.mjs enc|dec [scheme] [char-sep]  (stdin -> stdout) via CyberChef "To BCD" / "From BCD"
// enc: each char's decimal char code -> To BCD (packed, unsigned, Nibbles), chars joined by char-sep (default " / ")
// dec: split on char-sep, From BCD (Nibbles) each group -> decimal char code -> char
const base = process.env.CC + "/src/core/operations/";
const [mode, scheme = "8 4 2 1", sep = " / "] = process.argv.slice(2);
const Op = (await import(base + (mode === "enc" ? "ToBCD.mjs" : "FromBCD.mjs"))).default;
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const BigNumber = (await import(process.env.CC + "/../bignumber.js/dist/bignumber.mjs")).default;
const op = new Op();
if (mode === "enc") {
    process.stdout.write([...input].map(c => op.run(new BigNumber(c.codePointAt(0)), [scheme, true, false, "Nibbles"])).join(sep));
} else {
    process.stdout.write(input.split(sep).map(g => String.fromCodePoint(Number(op.run(g, [scheme, true, false, "Nibbles"])))).join(""));
}
