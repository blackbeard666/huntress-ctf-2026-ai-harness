  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_4e9d6e94 = "c2ptLjU0ZmU2MjA0OWU0Mi1lZ2F0cy4vZWRvbi1zc2VydG51aC9wbXQvPWh0YXBfZWxpZnw2MjA0OUU0Mi1FRE9OPWRpX25naWFwbWFjfDE9dG51b2NfZWdhdHN8ZWxpZl9vdF95YXJyYV9kZXB5dD1yZXRwYWRhfGVsaWZfZXRpcncsZGVkZGVibWVfZWRvY2VkPXNwZXRzfDE9dg==";
  const Codec_4e9d6e94 = "base64_chunks|reverse_bytes|";

  function load_4e9d6e94() { return [...Buffer.from(Material_4e9d6e94, "base64")]; }
  function decode_4e9d6e94(EnCoDeD) { return [...EnCoDeD].reverse(); }
  async function recover_4e9d6e94() {
    const NeUtRaL = [3, 5, 8, 13].slice(1, 3);
    const EnCoDeD = load_4e9d6e94(); let DeCoDeD = [];
    DeCoDeD = decode_4e9d6e94(EnCoDeD);
    void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
  }
  async function inspect_4e9d6e94() { return Buffer.from(await recover_4e9d6e94(), "utf8").toString("utf8"); }
  async function plan_4e9d6e94() { const inspect = inspect_4e9d6e94; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "typed_array_to_file", destination: fields.file_path, api: "fs.writeFile" }); }
  void moduleShape; void plan_4e9d6e94;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_4e9d6e94());
