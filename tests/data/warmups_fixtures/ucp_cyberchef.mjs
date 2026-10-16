// usage: node ucp_cyberchef.mjs enc <prefix> [padding] [lower] | dec <prefix>   (stdin -> stdout)
// via CyberChef "Escape Unicode Characters" (Encode all chars) / "Unescape Unicode Characters"; prefix \u, %u or U+
const base = process.env.CC + "/src/core/operations/";
const [mode, prefix, pad, lower] = process.argv.slice(2);
const input = (await new Promise(r => { let d = ""; process.stdin.setEncoding("utf8"); process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
if (mode === "enc") {
  const Op = (await import(base + "EscapeUnicodeCharacters.mjs")).default;
  process.stdout.write(new Op().run(input, [prefix, true, parseInt(pad || "4"), lower !== "lower"]));
} else {
  const Op = (await import(base + "UnescapeUnicodeCharacters.mjs")).default;
  process.stdout.write(new Op().run(input, [prefix]));
}
