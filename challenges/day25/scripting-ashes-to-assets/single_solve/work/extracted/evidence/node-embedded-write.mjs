  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_96481092 = "\\u0060\\u0027\\u001b\\u0066\\u005d\\u005e\\u004f\\u005a\\u005d\\u0027\\u004e\\u004f\\u004d\\u0059\\u004e\\u004f\\u0049\\u004f\\u0057\\u004c\\u004f\\u004e\\u004e\\u004f\\u004e\\u0016\\u0061\\u005c\\u0053\\u005e\\u004f\\u0049\\u0050\\u0053\\u0056\\u004f\\u0066\\u004b\\u004e\\u004b\\u005a\\u005e\\u004f\\u005c\\u0027\\u005e\\u0063\\u005a\\u004f\\u004e\\u0049\\u004b\\u005c\\u005c\\u004b\\u0063\\u0049\\u005e\\u0059\\u0049\\u0050\\u0053\\u0056\\u004f\\u0066\\u005d\\u005e\\u004b\\u0051\\u004f\\u0049\\u004d\\u0059\\u005f\\u0058\\u005e\\u0027\\u001b\\u0066\\u004d\\u004b\\u0057\\u005a\\u004b\\u0053\\u0051\\u0058\\u0049\\u0053\\u004e\\u0027\\u0038\\u0039\\u002e\\u002f\\u0017\\u0022\\u002b\\u0022\\u001c\\u002d\\u001c\\u0030\\u001a\\u0066\\u0050\\u0053\\u0056\\u004f\\u0049\\u005a\\u004b\\u005e\\u0052\\u0027\\u0019\\u005e\\u0057\\u005a\\u0019\\u0052\\u005f\\u0058\\u005e\\u005c\\u004f\\u005d\\u005d\\u0017\\u0058\\u0059\\u004e\\u004f\\u0019\\u0018\\u005d\\u005e\\u004b\\u0051\\u004f\\u0017\\u0022\\u004b\\u0022\\u001c\\u004d\\u001c\\u0050\\u001a\\u004c\\u001b\\u004e\\u004b\\u0018\\u0057\\u0054\\u005d";
  const Codec_96481092 = "unicode_escapes|subtract_modulo_256|16";

  function load_96481092() { return [...Material_96481092.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_96481092(v_a19c) { return v_a19c.map((value) => (value + 22) & 255); }
  async function recover_96481092() {
    const v_c304 = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
    const v_a19c = load_96481092(); let v_b27e = [];
    for (const v_d41a of [1]) v_b27e = decode_96481092(v_a19c);
    void v_c304; return Buffer.from(v_b27e).toString("ascii");
  }
  async function inspect_96481092() { return ({ ...{ value: await recover_96481092() } }).value; }
  async function plan_96481092() { const inspect = inspect_96481092; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "typed_array_to_file", destination: fields.file_path, api: "fs.writeFile" }); }
  void moduleShape; void plan_96481092;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_96481092());
