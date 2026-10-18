// usage: node twosym_index_cyberchef.mjs <sym0> <sym1> <width> <b32|b64|b64url|octal>  (stdin -> stdout)
// symbols -> 0/1 (whitespace dropped), CyberChef 'From Binary' (Byte Length=width) -> group values;
// b32/b64/b64url: each value indexes the alphabet -> CyberChef 'From Base32' / 'From Base64';
// octal: values are octal digits, 3 per byte -> CyberChef 'From Octal'. Result decoded as UTF-8.
const base = process.env.CC + "/src/core/operations/";
const [s0, s1, width, inner] = process.argv.slice(2);
const op = async n => new (await import(base + n + ".mjs")).default();
const input = (await new Promise(r => { let d = ""; process.stdin.on("data", c => d += c); process.stdin.on("end", () => r(d)); })).replace(/\n$/, "");
const bits = Array.from(input).filter(c => !/\s/.test(c)).map(c => c === s0 ? "0" : c === s1 ? "1" : "?").join("");
const vals = (await op("FromBinary")).run(bits, ["None", Number(width)]);
const B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
let bytes;
if (inner === "b32") {
    const s = vals.map(v => "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"[v]).join("");
    bytes = (await op("FromBase32")).run(s, ["A-Z2-7=", true]);
} else if (inner === "octal") {
    const d = vals.join(""), groups = d.match(/.{3}/g).join(" ");
    bytes = (await op("FromOctal")).run(groups, ["Space"]);
} else {
    const al = B64 + (inner === "b64url" ? "-_" : "+/");
    bytes = (await op("FromBase64")).run(vals.map(v => al[v]).join(""),
        [inner === "b64url" ? "A-Za-z0-9-_" : "A-Za-z0-9+/=", true, false]);   // CyberChef range syntax
}
process.stdout.write(new TextDecoder("utf-8", { fatal: true }).decode(Uint8Array.from(bytes)));
