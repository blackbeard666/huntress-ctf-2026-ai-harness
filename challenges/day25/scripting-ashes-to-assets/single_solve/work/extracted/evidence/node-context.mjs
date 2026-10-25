// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_664856db = "8c534792898a7b8689537a7b79857a7b757985847c7f7d8b88778a7f858442887b8a8b8884757985847c7f7d8b88778a7f858492777a77868a7b88537c8885907b84758578807b798a92898a777d7b7579858b848a53479279778386777f7d84757f7a5364655a5b434f4c5a49584c5c5a927e85898a757f7a537e85898a434f4c7a49784c7c7a77484978";
const Codec_664856db = "hex_buffer|add_modulo_256|16";

function load_664856db() { return [...Buffer.from(Material_664856db, "hex")]; }
function decode_664856db(v_a19c) { return v_a19c.map((value) => (value - 22 + 256) & 255); }
async function recover_664856db() {
  const v_c304 = [3, 5, 8, 13].slice(1, 3);
  const v_a19c = load_664856db(); let v_b27e = [];
  switch (1) { case 1: v_b27e = decode_664856db(v_a19c); break; default: throw new Error("state"); }
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_664856db() { return Buffer.from(await recover_664856db(), "utf8").toString("utf8"); }
async function plan_664856db() { const inspect = inspect_664856db; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_664856db;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_664856db());

// reconstruction complete