// Independent snappy oracle: stdin = snappy framing-format stream (or a raw block with --raw) -> stdout bytes.
// Raw blocks are decoded by the npm `snappyjs` package (tools/npm-snappyjs); framing chunks split here per the spec.
const path = require("path");
const SnappyJS = require(path.join(__dirname, "../../../tools/npm-snappyjs/node_modules/snappyjs"));
const b = require("fs").readFileSync(0);
if (process.argv.includes("--raw")) { process.stdout.write(Buffer.from(SnappyJS.uncompress(b))); process.exit(0); }
if (b.slice(0, 10).toString("latin1") !== "\xff\x06\x00\x00sNaPpY") { console.error("no stream id"); process.exit(1); }
const T = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? (c >>> 1) ^ 0x82F63B78 : c >>> 1; T.push(c >>> 0); }
const crc = (d) => { let c = 0xFFFFFFFF; for (const x of d) c = T[(c ^ x) & 0xFF] ^ (c >>> 8); c = (c ^ 0xFFFFFFFF) >>> 0;
  return ((((c >>> 15) | (c << 17)) >>> 0) + 0xA282EAD8) >>> 0; };
const out = [];
for (let i = 0; i < b.length;) {
  const t = b[i], n = b[i + 1] | b[i + 2] << 8 | b[i + 3] << 16, body = b.slice(i + 4, i + 4 + n);
  if (body.length !== n) { console.error("truncated"); process.exit(1); }
  if (t === 0 || t === 1) {
    const d = t === 0 ? Buffer.from(SnappyJS.uncompress(body.slice(4))) : body.slice(4);
    if (crc(d) !== body.readUInt32LE(0)) { console.error("bad CRC-32C"); process.exit(1); }
    out.push(d);
  }
  else if (t !== 0xff && t < 0x80) { console.error("reserved chunk"); process.exit(1); }
  i += 4 + n;
}
process.stdout.write(Buffer.concat(out));
