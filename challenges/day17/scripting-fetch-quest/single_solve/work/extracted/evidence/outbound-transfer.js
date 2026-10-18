// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decodeBase64(text) {
  var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  var clean = text.replace(/[^A-Za-z0-9+\/=]/g, "");
  var output = [];
  for (var p = 0; p < clean.length; p += 4) {
    var a = alphabet.indexOf(clean.charAt(p));
    var b = alphabet.indexOf(clean.charAt(p + 1));
    var c = clean.charAt(p + 2) == "=" ? -1 : alphabet.indexOf(clean.charAt(p + 2));
    var d = clean.charAt(p + 3) == "=" ? -1 : alphabet.indexOf(clean.charAt(p + 3));
    output.push((a << 2) | (b >> 4));
    if (c >= 0) output.push(((b & 15) << 4) | (c >> 2));
    if (d >= 0) output.push(((c & 3) << 6) | d);
  }
  return output;
}
function decode_d97a16b8(v_a19c) {
  var v_b27e = [];
  var previous = 191;
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ previous); previous = v_a19c[i]; }
  return v_b27e;
}
function recover_34a14ffb() {
  var packedText = "xOaV4YT0h6WfxOaK5Ybnk/apxarJqMTmyuiY6o//nuyJ1qLQsd+syq/d/9PxhPSY95byrd+617jMqYvW+ti53bzMuN2vjbeV1rnXsdi/7In" + "qn+2E8InZttqz0KmH4pr/3fHTpcSo3bjL6dOoiumI5ZX0nfqUy6LG5N78n/6T44LrjOLPrJ6mkaaWpMb3zuzA4pfliauRs9uv26vY4s3igb" + "OLvIu7ieva482o0LHcrMCli+KM+pv3nvrVs4e2hLDUsNT6nv+LqYWn0qHEtumI74rkkLKIquKX+Y3/muma1rfV+pmrk6STo5HzwvvZ9dex2" + "LTRjv6f64Ohm7n6wJzAleaD8YLegtKnxanAo/+j657whPaT4JPfvtyA3K/but24lfbE/Mv8zP6crZS63r/L6ZS4mumd/Jv+vdKnyb2fpZbr";

  var v_a19c = decodeBase64(packedText);

  var v_f602 = [3, 5, 8, 13].slice(1, 3);

  var v_b27e = [];

  var pass = 0;

  while (pass < 1) { v_b27e = decode_d97a16b8.apply(null, [v_a19c]); pass++; }

  var v_c304 = "", bi = 0;

  for (bi = 0; bi < v_b27e.length; bi++) { v_c304 += String.fromCharCode(v_b27e[bi]); }

  return v_c304;
}
function inspect_b32831f3() {
  var v_d41a = eval("(" + recover_34a14ffb.apply(null, []) + ")");
  return { steps: v_d41a.steps, adapter: v_d41a.adapter, values: v_d41a.values, stageCount: v_d41a.stageCount };
}
