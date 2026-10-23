// Independent reader for saml-redirect fixtures: WHATWG-style query split + decodeURIComponent + Node Buffer base64 +
// node:zlib inflateRawSync / inflateSync / gunzipSync. Prints the inflated text, or "None" when nothing inflates.
// usage: node saml_redirect_oracle.mjs "<encoded>"
import zlib from "node:zlib";
const s = process.argv[2].trim();
const q = s.includes("?") ? s.slice(s.indexOf("?") + 1) : s;
const vals = q.split("&").map((kv) => (kv.includes("=") && /^[A-Za-z_]/.test(kv) && kv.indexOf("=") < kv.length - 2
  ? kv.slice(kv.indexOf("=") + 1) : kv));
vals.push(s);
for (const v of vals) {
  let u;
  try { u = decodeURIComponent(v); } catch { continue; }
  if (!/^[A-Za-z0-9+/]+={0,2}$/.test(u)) continue;
  const b = Buffer.from(u, "base64");
  for (const f of [zlib.inflateRawSync, zlib.inflateSync, zlib.gunzipSync]) {
    try { process.stdout.write(f(b).toString("utf8")); process.exit(0); } catch {}
  }
}
process.stdout.write("None");
