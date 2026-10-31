  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_b7f43fd5 = "\\u0076\\u003d\\u0031\\u007c\\u0073\\u0074\\u0065\\u0070\\u0073\\u003d\\u0061\\u0063\\u0071\\u0075\\u0069\\u0072\\u0065\\u005f\\u0072\\u0065\\u006d\\u006f\\u0074\\u0065\\u002c\\u0064\\u0069\\u0073\\u0070\\u0061\\u0074\\u0063\\u0068\\u005f\\u006d\\u0065\\u006d\\u006f\\u0072\\u0079\\u007c\\u0061\\u0064\\u0061\\u0070\\u0074\\u0065\\u0072\\u003d\\u0068\\u0074\\u0074\\u0070\\u005f\\u0074\\u0068\\u0065\\u006e\\u005f\\u006d\\u006f\\u0064\\u0075\\u006c\\u0065\\u007c\\u0073\\u0074\\u0061\\u0067\\u0065\\u005f\\u0063\\u006f\\u0075\\u006e\\u0074\\u003d\\u0031\\u007c\\u0063\\u0061\\u006d\\u0070\\u0061\\u0069\\u0067\\u006e\\u005f\\u0069\\u0064\\u003d\\u004e\\u004f\\u0044\\u0045\\u002d\\u0041\\u0044\\u0033\\u0041\\u0043\\u0044\\u0036\\u0038\\u007c\\u0075\\u0072\\u006c\\u003d\\u0068\\u0074\\u0074\\u0070\\u0073\\u003a\\u002f\\u002f\\u006e\\u006f\\u0064\\u0065\\u002d\\u0061\\u0064\\u0033\\u0061\\u0063\\u0064\\u0036\\u0038\\u0062\\u0037\\u0062\\u0062\\u002e\\u0065\\u0078\\u0061\\u006d\\u0070\\u006c\\u0065\\u002e\\u0069\\u006e\\u0076\\u0061\\u006c\\u0069\\u0064\\u002f\\u0061\\u0070\\u0069\\u007c\\u0075\\u0073\\u0065\\u0072\\u005f\\u0061\\u0067\\u0065\\u006e\\u0074\\u003d\\u004e\\u006f\\u0064\\u0065\\u0041\\u0075\\u0064\\u0069\\u0074\\u002f\\u0061\\u0064\\u0033\\u0061";
  const Codec_b7f43fd5 = "unicode_escapes|identity|";

  function load_b7f43fd5() { return [...Material_b7f43fd5.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_b7f43fd5(storedBytes) { return [...storedBytes]; }
  async function recover_b7f43fd5() {
    const [harmlessValue] = ["compass"];
    const storedBytes = load_b7f43fd5(); let recoveredBytes = [];
    const decodeTarget = decode_b7f43fd5; recoveredBytes = decodeTarget(storedBytes);
    void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
  }
  async function inspect_b7f43fd5() { return (await recover_b7f43fd5()).split("|").join("|"); }
  async function plan_b7f43fd5() { const inspect = inspect_b7f43fd5; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "http_then_module", url: fields.url, dispatch: "vm.Script" }); }
  void moduleShape; void plan_b7f43fd5;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_b7f43fd5());
