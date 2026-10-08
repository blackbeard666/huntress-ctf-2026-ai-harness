  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_c973e216 = "[\"c3\",\"91\",\"c2\",\"c2\",\"90\",\"c3\",\"95\",\"92\",\"c5\",\"97\",\"96\",\"9e\",\"8a\",\"d3\",\"d4\",\"c8\",\"cf\",\"9a\",\"c3\",\"ce\",\"f8\",\"d3\",\"d4\",\"c8\",\"cf\",\"db\",\"90\",\"e3\",\"95\",\"92\",\"e5\",\"97\",\"96\",\"9e\",\"8a\",\"e2\",\"e3\",\"e8\",\"e9\",\"9a\",\"c3\",\"ce\",\"f8\",\"c9\",\"c0\",\"ce\",\"c6\",\"d7\",\"ca\",\"c6\",\"c4\",\"db\",\"96\",\"9a\",\"d3\",\"c9\",\"d2\",\"c8\",\"c4\",\"f8\",\"c2\",\"c0\",\"c6\",\"d3\",\"d4\",\"db\",\"d3\",\"d5\",\"c8\",\"d7\",\"c2\",\"d5\",\"f8\",\"c2\",\"cb\",\"c8\",\"d4\",\"c9\",\"c8\",\"c4\",\"9a\",\"d5\",\"c2\",\"d3\",\"d7\",\"c6\",\"c3\",\"c6\",\"db\",\"c9\",\"c8\",\"ce\",\"d3\",\"c6\",\"d5\",\"d2\",\"c0\",\"ce\",\"c1\",\"c9\",\"c8\",\"c4\",\"f8\",\"c9\",\"d5\",\"d2\",\"d3\",\"c2\",\"d5\",\"8b\",\"c9\",\"c8\",\"ce\",\"d3\",\"c6\",\"d5\",\"d2\",\"c0\",\"ce\",\"c1\",\"c9\",\"c8\",\"c4\",\"f8\",\"c2\",\"c3\",\"c8\",\"c4\",\"c2\",\"c3\",\"9a\",\"d4\",\"d7\",\"c2\",\"d3\",\"d4\",\"db\",\"96\",\"9a\",\"d1\"]";
  const Codec_c973e216 = "hex_array|reverse_then_xor|a7";

  function load_c973e216() { return JSON.parse(Material_c973e216).map((value) => Number.parseInt(value, 16)); }
  function decode_c973e216(v_a19c) { return [...v_a19c].reverse().map((value) => value ^ 167); }
  async function recover_c973e216() {
    const [v_c304] = ["compass"];
    const v_a19c = load_c973e216(); let v_b27e = [];
    v_b27e = await (async () => decode_c973e216(v_a19c))();
    void v_c304; return Buffer.from(v_b27e).toString("ascii");
  }
  async function inspect_c973e216() { return (await recover_c973e216()).split("|").join("|"); }
  async function plan_c973e216() { const inspect = inspect_c973e216; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
  void moduleShape; void plan_c973e216;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_c973e216());
