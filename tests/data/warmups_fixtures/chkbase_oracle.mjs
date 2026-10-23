// Independent oracle for checksummed base-N fixtures: npm bech32@2 / bs58check@3 / base-x@4 (+ node:crypto sha256d).
// usage: printf %s "$encoded" | NM=$PWD/tools/npm-bech32/node_modules node chkbase_oracle.mjs <bech32|bech32m|b58check|ripplecheck|flickr>
import { createRequire } from "node:module";
import { createHash } from "node:crypto";
const req = createRequire(process.env.NM + "/");
const mode = process.argv[2];
const s = require0();
function require0() { return require("node:fs").readFileSync(0, "utf8").trim(); }
function require(m) { return req(m); }
const sha = (b) => createHash("sha256").update(b).digest();
let out;
if (mode === "bech32" || mode === "bech32m") {
  const lib = req("bech32")[mode];
  out = Buffer.from(lib.fromWords(lib.decode(s, 10000).words));
} else if (mode === "b58check") {
  const m = req("bs58check"); out = Buffer.from((m.default || m).decode(s)).subarray(1);
} else {
  const bx = req("base-x"); const basex = bx.default || bx;
  const A = mode === "flickr" ? "123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"
                              : "rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz";
  const b = Buffer.from(basex(A).decode(s));
  if (mode === "flickr") out = b;
  else {
    if (!sha(sha(b.subarray(0, -4))).subarray(0, 4).equals(b.subarray(-4))) throw new Error("bad checksum");
    out = b.subarray(1, -4);
  }
}
process.stdout.write(new TextDecoder("utf-8", { fatal: true }).decode(out));
