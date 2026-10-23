// usage: MF=<multiformats pkg dir> node b256emoji_multiformats.mjs [mb]  (stdin UTF-8 -> stdout) via npm multiformats
// bases/base256emoji: "mb" = multibase string (🚀 prefix, base256emoji.encode), else the bare baseEncode
const { base256emoji } = await import(process.env.MF + "/dist/src/bases/base256emoji.js");
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const b = new TextEncoder().encode(input);
process.stdout.write(process.argv[2] === "mb" ? base256emoji.encode(b) : base256emoji.baseEncode(b));
