// usage: node b85sweep_cyberchef.mjs std|z85|ipv6 [hexin]  (stdin -> stdout) via CyberChef "To Base85" with the
// "Standard" (!-u, 'z' for zero groups), "Z85 (ZeroMQ)" or "IPv6" (RFC 1924 alphabet, 4-byte groups) alphabet.
// hexin: stdin is hex of the raw bytes (for compressed / binary inner layers).
const base = process.env.CC + "/src/core/operations/";
const AL = { std: "!-u", z85: "0-9a-zA-Z.\\-:+=^!/*?&<>()[]{}@%$#", ipv6: "0-9A-Za-z!#$%&()*+\\-;<=>?@^_`{|}~" };
const Op = (await import(base + "ToBase85.mjs")).default;
let input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const bytes = process.argv[3] === "hexin" ? Uint8Array.from(Buffer.from(input.trim(), "hex")) : new TextEncoder().encode(input);
process.stdout.write(new Op().run(bytes.buffer, [AL[process.argv[2]], false]));
